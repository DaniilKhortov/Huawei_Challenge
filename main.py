from fastapi import FastAPI
from fastapi.responses import JSONResponse

from celery.result import AsyncResult
import uvicorn

from celery_app import darcy_optimization, celery_app


app = FastAPI()


@app.post("/optimize/", response_class=JSONResponse)
async def optimize(
    rho: float,
    cp: float,
    k_thermal: float,
    mu: float,
    k_fluid: float,
    ne: int,
    p_init: list[list[float]],
    t_init: list[list[float]],
    b: list[list[float]],
    n_tilde: list[list[float]], 
    x_l: float,
    x_u: float,
):
    result = darcy_optimization.delay(
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
    )
    return {"result_id": result.id}


@app.get("/results/{result_id}", response_class=JSONResponse)
async def get_result(result_id):
    result = AsyncResult(result_id, app=celery_app)

    is_ready = result.ready()
    is_succesful = result.successful()
    state = result.state

    if is_ready and is_succesful:
        data = result.result
    else:
        data = None

    return {
        "is_ready": is_ready, 
        "is_succesful": is_succesful, 
        "state": state,
        "data": data
    }


if __name__ == "__main__":
    uvicorn.run(app)