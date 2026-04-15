"""Insights / analytics response schema."""

from pydantic import BaseModel


class InsightsResponse(BaseModel):
    total_teams:                     int
    total_members:                   int
    teams_with_leader_not_colocated: int
    teams_with_nondir_leader:        int
    teams_nondir_ratio_above_20:     int
    teams_reporting_to_org_leader:   int
