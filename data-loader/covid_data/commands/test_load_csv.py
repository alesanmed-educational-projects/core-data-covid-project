import unittest
from unittest import TestCase
from unittest.mock import Mock, patch

from covid_data.errors import PlaceNameNotProvidedException
from covid_data.types import PlaceType
from covid_data.utils.places import get_place_info


class TestGetPlaceInfo(TestCase):
    def setUp(self) -> None:
        self.mock_place = {
            "results": [
                {
                    "components": {
                        "ISO_3166-1_alpha-2": "Test",
                        "ISO_3166-1_alpha-3": "Test",
                        "country": "Test",
                        "_type": "country",
                        "_category": "Test",
                    }
                }
            ]
        }

    def test_exception_when_no_name(self):
        """Should raise an exception when no place is passed"""
        self.assertRaises(
            PlaceNameNotProvidedException, get_place_info, None, PlaceType.COUNTRY
        )

    @patch("requests.get")
    def test_none_when_error(self, mock_get: Mock):
        """Should return None when the response code is an error"""
        mock_get.return_value.status_code = 400

        res = get_place_info("TestPlace", PlaceType.COUNTRY)

        self.assertIsNone(res)

    @patch("requests.get")
    def test_properties_renaming(self, mock_get: Mock):
        """Should rename properties in JSON response"""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = Mock(return_value=self.mock_place)

        try:
            get_place_info("Test", PlaceType.COUNTRY)
        except Exception:
            pass

        self.assertDictEqual(
            self.mock_place,
            {
                "results": [
                    {
                        "components": {
                            "alpha2": "Test",
                            "alpha3": "Test",
                            "type": "country",
                            "country": "Test",
                            "category": "Test",
                        }
                    }
                ]
            },
        )


if __name__ == "__main__":
    unittest.main()
