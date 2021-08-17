## Authentication

The endpoints endingw with `[A]` require authentication. You have to send a `Bearer Token` with a valid API key in the headers.

You can generate that key as explained in [README](README.md#api-key).

## Endpoints

The endpoints exposed by this API are:

```http
POST /auth [A] 
```

Checks whether the API key is valid or not.

```http
GET /cases
```

Returns COVID cases according to several filters:

- `type`: Case type. Valids are `recovered`, `confirmed`, `dead`
- `agg`: Aggregation fields. Valids are `date`, `country`, `type`, `province`, `province_code`
- `resultType`: Accumulation type. Valids are `cummulativeDate`, `cummulativeDateCountry`, `cummulativeCountry`, `cummulativeProvince`
- `country`: Only cases belonging to this country
- `province`: Only cases belonging to this province
- `date`: Only cases from this exact date
- `date[gte]`: Only cases newer than this date
- `date[lte]`: Only cases older than this date
- `limit`: Max number of cases to return
- `sort`: Fields to use for sorting, in shape `[field, -other]`
- `normalize`: Whether to normalize the `amount` column or not

```http
GET /countries
```

Returns countries according several filters:

- `name`: Coutry name
- `near`: Latitude and Longitude separated by comma. The results are sorted according to the distance to that point.

```http
POST /countries [A]
```

Creates a new country with the body data. The body has to be JSON with all fields required:

```json
{
    "name": "Country",
    "alpha2": "CR",
    "alpha3": "COU",
    "lat": "37.401875",
    "lng": "-5.9890039"
}
```

```http
GET /countries/:id/provinces
```

Return the provinces (states) from the country with requested ID.

```http
POST /email
```

Sends an email with the PDF present in the body. It has to be a `form-data` with the PDF in `files` and the recipient email in `recipient`.

```http
GET /provinces
```

Returns all provinces
