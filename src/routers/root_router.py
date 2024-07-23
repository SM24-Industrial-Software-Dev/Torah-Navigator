from fastapi import APIRouter, HTTPException
from typing import Dict
from ..logging_config import setup_logging
from src.models.content_handler import ContentHandler
from src.models.trending import Trending

router = APIRouter()
content_filtering = ContentHandler()
trending = Trending()


logger = setup_logging()


@router.get("/content-recommendations/{user_id}", response_model=Dict[int, str])
def get_content_recommendations(user_id: int, top_n: int = 10):
    try:
        recommendations = content_filtering.recommend_for_user_content(
            user_id, top_n)
        return recommendations
    except KeyError:
        logger.error(
            f"Shiur ID {user_id} not found in the similarity matrix.")
        raise HTTPException(status_code=404, detail="Shiur ID not found")


@router.get("/because-you-listened-recommendations/{user_id}", response_model=Dict[int, str])
def get_because_you_listened_recommendations(user_id: int, top_n: int = 5):
    try:
        recommendations = content_filtering.recommend_based_on_recent_activity(
            user_id, top_n)
        return recommendations
    except KeyError:
        logger.error(
            f"Shiur ID {user_id} not found in the similarity matrix.")
        raise HTTPException(status_code=404, detail="Shiur ID not found")
    
@router.get("/trending",response_model=Dict[int,str])
def get_trending(top_n: int = 5 , past_days: int = 7):
    recommendations = trending.get_trending(top_n=top_n,past_days=past_days)
    return recommendations

@router.get("/trending/filtered/{feature_key}={feature_value}",response_model=Dict[int,str])
def get_trending_filtered(feature_key,feature_value, top_n: int = 5, past_days: int = 7):
    try:
        recommendations = trending.get_trending_filtered(top_n,past_days,feature_key,feature_value)
        return recommendations
    except KeyError:
        logger.error(
            f"Key-Value {feature_key}={feature_value} not found.")
        raise HTTPException(status_code=404, detail="Key-Value pair not found")