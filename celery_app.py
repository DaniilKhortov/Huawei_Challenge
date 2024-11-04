from celery import Celery
import numpy as np

from darcy import Darcy, simp

celery_app = Celery("main", broker="redis://redis", backend="redis://redis")


@celery_app.task
def darcy_optimization(
    rho,
    cp,
    k_thermal,
    mu,
    k_fluid,
    ne,
    p_init,
    t_init,
    b,
    n_tilde,
    x_l,
    x_u
):
    darcy = Darcy(
        rho, 
        cp, 
        k_thermal, 
        mu, 
        k_fluid, 
        ne, 
        x_l, 
        x_u, 
        np.array(p_init), 
        np.array(t_init), 
        np.array(b), 
        np.array(n_tilde)
    )
    
    rho = np.random.uniform(0.001, 1, size=ne)
    Kc, comp = simp(rho, darcy.k_thermal, darcy, {})

    return {"Kc": Kc.tolist(), "compliance": comp}