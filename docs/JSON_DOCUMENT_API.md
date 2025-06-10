# JSON Document API

This document describes the API endpoints for working with JSON documents. Each document now includes a required `name` field.

## Create Document

`POST /json-document`

Request body:
```json
{
  "name": "My Document",
  "data": { }
}
```

## Get Document

`GET /json-document/{document_id}`

Response body includes the `name` field:
```json
{
  "document_id": "uuid",
  "name": "My Document",
  "data": { },
  "org_id": "org",
  "created_at": 0,
  "updated_at": 0,
  "is_public": false
}
```

## Update Document

`POST /json-document/{document_id}`

Request body (any field optional):
```json
{
  "name": "New Name",
  "data": { }
}
```

## List Documents

`GET /json-documents?org_id={id}`

Each returned item contains a `name`.

Existing documents without a name will automatically receive the placeholder `"Document {id}"` when retrieved.
