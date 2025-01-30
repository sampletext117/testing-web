from dataclasses import dataclass


@dataclass
class CampaignProgram:
    campaign_program_id: int
    candidate_id: int
    description: str
