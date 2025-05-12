from fastapi import APIRouter

router = APIRouter()

@router.get('/predictions')
async def get_predictions():
    return {'message': 'Prediction endpoint'}
