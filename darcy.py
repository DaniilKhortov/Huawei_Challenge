import numpy as np
from scipy.integrate import quad_vec


class Darcy:
    def __init__(
        self, 
        rho, 
        cp, 
        k_thermal, 
        mu, 
        k_fluid, 
        ne, 
        x_l, 
        x_u, 
        p_init, 
        t_init,
        b,
        n_tilde,
        # k0
    ):
        self.rho = rho
        self.cp = cp
        self.k_thermal = k_thermal
        self.mu = mu
        self.k_fluid = k_fluid
        self.ne = ne
        self.x_l = x_l
        self.x_u = x_u
        self.p_init = p_init
        self.t_init = t_init
        self.b = b
        self.n_tilde = n_tilde
        # self.k0 = k0

        self.f_inlet = Darcy.inlet_pressure_load(k_fluid, p_init)
        self.p_nodes = Darcy.nodal_pressure(k_fluid, self.f_inlet)
        self.p_diff = np.diff(self.p_nodes, axis=0)
        self.u_flow = Darcy.fluid_velocity(k_fluid, mu, self.p_diff)
        self.Cp = Darcy.convection_matrix(
            ne, 
            rho, 
            cp, 
            self.u_flow.mean(), 
            self.n_tilde, 
            self.b, 
            x_l, 
            x_u
        )


    def __call__(self, rho, coeff):
        Kc = Darcy.update_conductivity_matrix(
            self.ne, self.k_thermal, rho, coeff, self.b, self.x_l, self.x_u
        )
        t_final = Darcy.thermal_steady_state_heat_transfer(
            Kc, self.Cp, self.t_init
        )
        compliance = Darcy.global_thermal_compilance(self.t_init, t_final)

        return Kc, compliance


    @staticmethod
    def inlet_pressure_load(
        k: np.matrix, # Permeability matrix
        p: np.float64 # Nodal pressure in the structure
    ):
        return k * p


    # flow solution
    @staticmethod
    def nodal_pressure(
        k: np.matrix, # Permeability matrix
        f: np.matrix # Pressure load at the inlet
    ):
        return np.dot(k, f ** -1)


    @staticmethod
    def fluid_velocity(
        k: np.float64, # Fluid permeability
        u: np.float64, # Fluid dynamic viscosity
        p_dif: np.float64 # Pressure differential
    ):
        return - k / u * p_dif


    @staticmethod
    def fluid_velocity_e(
        k: np.float64, # Fluid permeability
        u: np.float64, # Fluid dynamic viscosity
        b_dif: np.float64, # Differential of the shape function
        p_e: np.float64 # Nodal pressure in the element
    ):
        return - k / u * b_dif * p_e


    @staticmethod
    def conductivity_matrix_node(
        x: np.float64,
        # y: np.float64,
        k: np.float64, # Thermal conductivity
        b: np.matrix # Differential of the shape function
    ):
        return k * np.dot(b.T, b)


    @staticmethod
    def conductivity_matrix(
        ne: np.float64, # Total number of elements
        k: np.float64, # Thermal conductivity
        b: np.matrix, # Differential of the shape function
        x_l: np.float64,
        x_u: np.float64
    ):
        b_shape = b.shape[0]
        kc = np.zeros((b_shape, b_shape))
        for n in range(ne):
            res, _ = quad_vec(
                Darcy.conductivity_matrix_node, 
                x_l, 
                x_u, 
                args=(k, b)
            )
            kc += res

        return kc


    @staticmethod
    def convection_matrix_node(
        x: np.float64,
        # y: np.float64,
        rho: np.float64, # Density
        cp: np.float64, # Specific heat capacity
        u_e: np.float64, # Element flow velocity from Darcy’s Law
        n_t: np.matrix, # Enhanced shape function
        b: np.matrix # Differential of the shape function
    ):
        return rho * cp * np.dot(n_t.T, b) * u_e


    @staticmethod
    def convection_matrix(
        ne: np.float64, # Total number of elements
        rho: np.float64, # Density
        cp: np.float64, # Specific heat capacity
        u_e: np.float64, # Element flow velocity from Darcy’s Law
        n_t: np.matrix, # Enhanced shape function
        b: np.matrix, # Differential of the shape function
        x_l: np.float64,
        x_u: np.float64
    ):  
        n_t_shape = n_t.shape[1]
        cpm = np.zeros((n_t_shape, n_t_shape))
        for n in range(ne):
            res, _ = quad_vec(
                Darcy.convection_matrix_node, 
                x_l, 
                x_u, 
                args=(rho, cp, u_e, n_t, b)
            )
            cpm += res

        return cpm


    @staticmethod
    def thermal_steady_state_heat_transfer(
        kc: np.matrix, # Conductivity Matrix
        cp: np.matrix, # Convection Matrix
        t: np.matrix # Nodal temperature matrix
    ):
        return np.dot(kc + cp, t)


    @staticmethod
    def global_thermal_compilance(
        t: np.matrix, # Nodal temperature matrix
        f: np.matrix # Termal steady-state heat transfer
    ):
        return 0.5 * np.dot(t.T, f).item()


    @staticmethod
    def update_conductivity_matrix(ne, k0, rho, coeff, b, x_l, x_u):
        ke = rho ** coeff * k0
        kc = Darcy.conductivity_matrix(ne, ke, b, x_l, x_u)
        return kc
    

def simp(
    rho: np.matrix,
    k0: np.float64,
    obj_func,
    args,
    p = 3,
    iterations = 20,
    learning_rate = 0.1
):
    prep_compliance = 0

    for _ in range(iterations):
        args |= {"rho": rho}
        Kc, compliance = obj_func(coeff=p, **args)

        dC_drho = -p * rho ** (p - 1) * k0 * compliance # / (compliance + 1e-6)
        rho -= learning_rate * dC_drho
        rho = np.clip(rho, 0.01, 1)

        if np.abs(compliance - prep_compliance) < 0.0001:
            break
        else:
            prep_compliance = compliance

    return Kc, compliance