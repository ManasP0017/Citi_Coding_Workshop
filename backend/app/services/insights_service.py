"""Insights / analytics business logic — answers all 6 business questions."""

from sqlalchemy.orm import Session

from app.models.team import Team
from app.models.member import Member


def get_insights(db: Session) -> dict:
    teams   = db.query(Team).all()
    members = db.query(Member).all()

    member_map: dict[str, list[Member]] = {}
    for m in members:
        member_map.setdefault(m.team_id, []).append(m)

    teams_with_leader_not_colocated = 0
    teams_with_nondir_leader        = 0
    teams_nondir_ratio_above_20     = 0
    teams_reporting_to_org_leader   = 0

    for team in teams:
        team_members = member_map.get(team.id, [])
        leader = next((m for m in team_members if m.is_team_leader), None)

        if leader:
            if any(
                m.location and m.location != leader.location
                for m in team_members
                if not m.is_team_leader
            ):
                teams_with_leader_not_colocated += 1

            if not leader.is_direct_staff:
                teams_with_nondir_leader += 1

        if team_members:
            non_direct_count = sum(1 for m in team_members if not m.is_direct_staff)
            if non_direct_count / len(team_members) > 0.20:
                teams_nondir_ratio_above_20 += 1

        if team.organization_leader_id:
            teams_reporting_to_org_leader += 1

    return {
        "total_teams":                      len(teams),
        "total_members":                    len(members),
        "teams_with_leader_not_colocated":  teams_with_leader_not_colocated,
        "teams_with_nondir_leader":         teams_with_nondir_leader,
        "teams_nondir_ratio_above_20":      teams_nondir_ratio_above_20,
        "teams_reporting_to_org_leader":    teams_reporting_to_org_leader,
    }
