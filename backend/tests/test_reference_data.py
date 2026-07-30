import uuid

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.api.routes.medical_specialties import UserSpecialtiesInput
from app.services.location_service import municipalities, normalize_state, normalize_text, validate_location, validate_state


def test_all_27_official_states_and_normalization():
    assert len({city['state'] for city in municipalities()}) == 27
    assert normalize_state('sp') == 'SP'
    assert normalize_state('São Paulo') == 'SP'
    assert validate_state('rj') == 'RJ'


def test_invalid_state_is_rejected():
    with pytest.raises(HTTPException) as error:
        validate_state('XX')
    assert error.value.status_code == 422


def test_valid_city_state_pair_returns_canonical_snapshot():
    assert validate_location('sp', 'sao paulo', '3550308') == ('SP', 'São Paulo', '3550308')


def test_city_from_another_state_is_rejected():
    with pytest.raises(HTTPException) as error:
        validate_location('SP', 'Rio de Janeiro', '3304557')
    assert error.value.status_code == 422


def test_city_search_normalization_ignores_accents_and_case():
    city = next(item for item in municipalities() if item['ibge_code'] == '3550308')
    assert normalize_text(city['name']) == normalize_text('SAO PAULO')


def test_primary_and_secondary_must_be_distinct():
    specialty_id = uuid.uuid4()
    with pytest.raises(ValidationError):
        UserSpecialtiesInput(primary_id=specialty_id, secondary_id=specialty_id)


def test_primary_and_secondary_accept_distinct_specialties():
    payload = UserSpecialtiesInput(primary_id=uuid.uuid4(), secondary_id=uuid.uuid4())
    assert payload.primary_id != payload.secondary_id
