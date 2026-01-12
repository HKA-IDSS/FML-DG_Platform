from federatedmlrest.api.models import proposal_models, group_models, strategy_models, member_models, \
    quality_requirements_models
from tests.unit.conftest import *


def test_create_proposal_200(client):
    payload = proposal_models.AddProposal(
        name='first_test_prop_name',
        proposer=members_json['_id'],
        group=group_json['_id'],
        strategy_id=strat_json['_id'],
        variant='configuration',
        variant_id=configurations_json['_id'],
        reasoning='why not'
    )
    response = client.post('/proposals',
                           data=payload.json())
    resp_dict = response.json()
    assert resp_dict["name"] == payload.name
    assert resp_dict["proposer"] == str(payload.proposer)
    assert resp_dict['group'] == str(payload.group)
    assert resp_dict['strategy_id'] == str(payload.strategy_id)
    assert resp_dict["variant"] == payload.variant
    assert resp_dict['variant_id'] == str(payload.variant_id)
    assert resp_dict['reasoning'] == payload.reasoning
    assert resp_dict['votes'] == []
    assert response.status_code == 200


def test_get_all_proposals(client):
    payload = proposal_models.AddProposal(
        name='first_test_prop_name',
        proposer=members_json['_id'],
        group='5bb3314919802578051ccf86',
        strategy_id='5bb3314919802578051ccf86',
        variant='configuration',
        variant_id='5bb3314919802578051ccf86',
        reasoning='why not'
    )
    response = client.get('/proposals')
    resp_dict = response.json()
    assert resp_dict[0]["name"] == payload.name
    assert response.status_code == 200


def test_voting_clear_winner(client):
    group = group_models.AddGroup(
        name='group a',
    )

    res = client.post('/groups', data=group.json())
    assert res.status_code == 200
    group_id = res.json()['_id']

    strat = strategy_models.AddStrategy(
        name="strat 1 of a",
    )

    res = client.post(f'/groups/{group_id}/strategies', data=strat.json())
    assert res.status_code == 200
    strat_id = res.json()['_id']

    members = [
        member_models.AddMember(
            name=f'member {m} of a',
            organization='orga'
        )
        for m in range(3)
    ]

    member_ids = []
    for member in members:
        res = client.post(f'/groups/{group_id}/members', data=member.json())
        assert res.status_code == 200
        member_ids.append(res.json()['_id'])

    qual_reqs = [
        quality_requirements_models.AddQualityRequirement(
            name=f'quality req {qual_req}',
            correctness=quality_requirements_models.Correctness(metric='bla', required_min_value=0,
                                                                required_max_value=2),
        )
        for qual_req in range(3)
    ]

    qr_ids = []
    for qual_req in qual_reqs:
        res = client.post(f'/groups/{group_id}/strategies/{strat_id}/quality_requirements', data=qual_req.json())
    assert res.status_code == 200
    qr_ids.append(res.json()['_id'])

    proposals = [
        proposal_models.AddProposal(
            name=f'proposal {idx}',
            proposer=member_id,
            group=group_id,
            strategy_id=strat_id,
            variant=proposal_models.ProposalType.QUALITY_REQUIREMENT,
            variant_id=variant_id,
            reasoning='this',
        )
        for member_id, variant_id, idx in zip(member_ids, qr_ids, range(3))
    ]

    proposal_ids = []
    for proposal in proposals:
        res = client.post('/proposals', data=proposal.json())
        assert res.status_code == 200
        proposal_ids.append(res.json()['_id'])

    for member_id in member_ids[1:]:
        vote = proposal_models.Vote(
            member=member_id,
            priority=1,
        )

        res = client.post(f'/proposals/{proposal_ids[0]}/votes', data=vote.json())
        assert res.status_code == 200

    res = client.get(f'/proposals/{strat_id}/count_votes',
                     params={'proposal_type': proposal_models.ProposalType.QUALITY_REQUIREMENT.value})
    assert res.status_code == 200
    res_dict = res.json()

    assert res_dict['winner'] == proposal_ids[0]


def test_voting_no_majority(client):
    group = group_models.AddGroup(
        name='group a',
    )

    res = client.post('/groups', data=group.json())
    assert res.status_code == 200
    group_id = res.json()['_id']

    strat = strategy_models.AddStrategy(
        name="strat 1 of a",
    )

    res = client.post(f'/groups/{group_id}/strategies', data=strat.json())
    assert res.status_code == 200
    strat_id = res.json()['_id']

    members = [
        member_models.AddMember(
            name=f'member {m} of a',
            organization='orga'
        )
        for m in range(3)
    ]

    member_ids = []
    for member in members:
        res = client.post(f'/groups/{group_id}/members', data=member.json())
        assert res.status_code == 200
        member_ids.append(res.json()['_id'])

    qual_reqs = [
        quality_requirements_models.AddQualityRequirement(
            name=f'quality req {qual_req}',
            correctness=quality_requirements_models.Correctness(metric='bla', required_min_value=0,
                                                                required_max_value=2),
        )
        for qual_req in range(3)
    ]

    qr_ids = []
    for qual_req in qual_reqs:
        res = client.post(f'/groups/{group_id}/strategies/{strat_id}/quality_requirements', data=qual_req.json())
    assert res.status_code == 200
    qr_ids.append(res.json()['_id'])

    proposals = [
        proposal_models.AddProposal(
            name=f'proposal {idx}',
            proposer=member_id,
            group=group_id,
            strategy_id=strat_id,
            variant=proposal_models.ProposalType.QUALITY_REQUIREMENT,
            variant_id=variant_id,
            reasoning='this is why',
        )
        for member_id, variant_id, idx in zip(member_ids, qr_ids, range(3))
    ]

    proposal_ids = []
    for proposal in proposals:
        res = client.post('/proposals', data=proposal.json())
        assert res.status_code == 200
        proposal_ids.append(res.json()['_id'])

    vote = proposal_models.Vote(
        member=member_ids[0],
        priority=1,
    )

    res = client.post(f'/proposals/{proposal_ids[0]}/votes', data=vote.json())
    assert res.status_code == 200

    res = client.get(f'/proposals/{strat_id}/count_votes',
                     params={'proposal_type': proposal_models.ProposalType.QUALITY_REQUIREMENT.value})
    assert res.status_code == 200
    res_dict = res.json()

    assert res_dict.get('winner') is None


def test_voting_tie(client):
    group = group_models.AddGroup(
        name='group a',
    )

    res = client.post('/groups', data=group.json())
    assert res.status_code == 200
    group_id = res.json()['_id']

    strat = strategy_models.AddStrategy(
        name="strat 1 of a",
    )

    res = client.post(f'/groups/{group_id}/strategies', data=strat.json())
    assert res.status_code == 200
    strat_id = res.json()['_id']

    members = [
        member_models.AddMember(
            name=f'member {m} of a',
            organization='orga'
        )
        for m in range(3)
    ]

    member_ids = []
    for member in members:
        res = client.post(f'/groups/{group_id}/members', data=member.json())
        assert res.status_code == 200
        member_ids.append(res.json()['_id'])

    qual_reqs = [
        quality_requirements_models.AddQualityRequirement(
            name=f'quality req {qual_req}',
            correctness=quality_requirements_models.Correctness(metric='bla', required_min_value=0,
                                                                required_max_value=2),
        )
        for qual_req in range(3)
    ]

    qr_ids = []
    for qual_req in qual_reqs:
        res = client.post(f'/groups/{group_id}/strategies/{strat_id}/quality_requirements', data=qual_req.json())
        assert res.status_code == 200
        qr_ids.append(res.json()['_id'])

    proposals = [
        proposal_models.AddProposal(
            name=f'proposal {idx}',
            proposer=member_id,
            group=group_id,
            strategy_id=strat_id,
            variant=proposal_models.ProposalType.QUALITY_REQUIREMENT,
            variant_id=variant_id,
            reasoning='this is why',
        )
        for member_id, variant_id, idx in zip(member_ids, qr_ids, range(3))
    ]

    proposal_ids = []
    for proposal in proposals:
        res = client.post('/proposals', data=proposal.json())
        assert res.status_code == 200
        proposal_ids.append(res.json()['_id'])

    for member_id, proposal_index in zip(member_ids, range(3)):
        vote = proposal_models.Vote(
            member=member_id,
            priority=1,
        )

        res = client.post(f'/proposals/{proposal_ids[proposal_index]}/votes', data=vote.json())
        assert res.status_code == 200

    res = client.get(f'/proposals/{strat_id}/count_votes',
                     params={'proposal_type': proposal_models.ProposalType.QUALITY_REQUIREMENT.value})
    assert res.status_code == 200
    res_dict = res.json()

    assert res_dict.get('winner') is None
