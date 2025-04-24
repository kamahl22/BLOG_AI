from fastapi import APIRouter

router = APIRouter()

@router.get('/blockchain')
async def get_blockchain():
    return {'message': 'Blockchain endpoint'}
