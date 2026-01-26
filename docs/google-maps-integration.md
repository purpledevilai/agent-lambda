# Google Maps Integration

## Overview

The Google Maps integration allows agents to search for places, get detailed location information, and compute routes between locations. This enables use cases like planning outings, finding restaurants, getting travel time estimates, and discovering points of interest.

Unlike the Gmail and Google Calendar integrations which use OAuth, the Google Maps tools use a simple API key for authentication.

## Setup

### 1. Google Cloud Project Setup

1. **Go to Google Cloud Console**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Select or create a project

2. **Enable Required APIs**
   - Navigate to "APIs & Services" > "Library"
   - Search for and enable:
     - **Places API (New)** - For place search and details
     - **Routes API** - For route computation and directions

3. **Create an API Key**
   - Go to "APIs & Services" > "Credentials"
   - Click "+ CREATE CREDENTIALS" > "API key"
   - Copy your new API key

4. **(Recommended) Restrict Your API Key**
   - Click on the API key to edit it
   - Under "API restrictions", select "Restrict key"
   - Select only "Places API (New)" and "Routes API"
   - Optionally add IP restrictions for security

### 2. Environment Variables

Add this environment variable to your Lambda:

```bash
GOOGLE_MAPS_API_KEY=your-api-key-here
```

### 3. Billing Note

Google Maps Platform requires billing to be enabled, but you get **$200/month free credit** which covers significant usage for personal assistant scenarios. You won't be charged unless you exceed that threshold.

## Agent Tools

### Tool Reference Summary

| Tool ID | Description |
|---------|-------------|
| `search_places` | Search for places using natural language queries |
| `get_place_details` | Get comprehensive details about a specific place |
| `compute_routes` | Calculate routes between locations with travel time estimates |

---

## search_places

Search for places using natural language queries. Returns places matching the query with details like name, address, rating, price level, and opening hours.

**Tool ID:** `search_places`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `text_query` | string | Yes | Natural language search query (see examples below) |
| `latitude` | float | No | Latitude for location bias |
| `longitude` | float | No | Longitude for location bias |
| `radius` | float | No | Search radius in meters (Google infers if not provided) |
| `min_rating` | float | No | Minimum rating filter (1.0 to 5.0) |
| `open_now` | bool | No | Only return places currently open |
| `price_levels` | array | No | Filter by price level(s) |
| `max_results` | int | No | Maximum results to return (default 10, max 20) |
| `rank_by` | string | No | Ranking preference: RELEVANCE, DISTANCE, or POPULARITY |

### text_query Examples

The `text_query` parameter is very flexible and can include:

| Query Type | Example |
|------------|---------|
| Place types | `"restaurants"`, `"coffee shops"`, `"museums"`, `"parks"` |
| Qualifiers | `"best sushi"`, `"cheap eats"`, `"fancy restaurants"` |
| Features | `"restaurants with outdoor seating"`, `"cafes with wifi"` |
| Location in text | `"pizza in downtown Austin"`, `"hotels near Central Park"` |
| Time-based | `"restaurants open late"`, `"brunch spots open on Sunday"` |
| Exact addresses | `"123 Main St, Austin, TX"` (returns coordinates and place ID) |
| Specific places | `"Empire State Building"`, `"Sydney Opera House"` |
| Combinations | `"highly rated Italian restaurants in San Francisco with outdoor seating"` |

### price_levels Values

- `PRICE_LEVEL_INEXPENSIVE` - $
- `PRICE_LEVEL_MODERATE` - $$
- `PRICE_LEVEL_EXPENSIVE` - $$$
- `PRICE_LEVEL_VERY_EXPENSIVE` - $$$$

### rank_by Values

- `RELEVANCE` - Best match for the query (default)
- `DISTANCE` - Closest first (requires latitude/longitude)
- `POPULARITY` - Most popular/well-known first

### Example Requests

**Find restaurants in a city:**
```json
{
  "text_query": "Italian restaurants in downtown Austin"
}
```

**Find highly-rated places near coordinates:**
```json
{
  "text_query": "coffee shops",
  "latitude": 30.2672,
  "longitude": -97.7431,
  "min_rating": 4.5,
  "open_now": true
}
```

**Get coordinates for an address:**
```json
{
  "text_query": "123 Congress Ave, Austin, TX"
}
```

**Find budget-friendly options:**
```json
{
  "text_query": "restaurants near Times Square",
  "price_levels": ["PRICE_LEVEL_INEXPENSIVE", "PRICE_LEVEL_MODERATE"],
  "max_results": 10
}
```

### Returns

```json
{
  "places": [
    {
      "id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
      "name": "Trattoria Lisina",
      "address": "123 Congress Ave, Austin, TX 78701",
      "location": {"latitude": 30.2655, "longitude": -97.7425},
      "rating": 4.7,
      "review_count": 1842,
      "price_level": "PRICE_LEVEL_MODERATE",
      "type": "Italian restaurant",
      "open_now": true,
      "hours": ["Monday: 11:00 AM – 10:00 PM", "Tuesday: 11:00 AM – 10:00 PM"],
      "phone": "(512) 555-0123",
      "website": "https://example.com",
      "google_maps_url": "https://maps.google.com/?cid=...",
      "description": "Upscale Italian eatery with handmade pasta and wine list."
    }
  ],
  "count": 1,
  "query": "Italian restaurants in Austin"
}
```

**Key Fields:**
- `id` - Google Place ID (use with `get_place_details` or `compute_routes`)
- `location` - Coordinates (use with `compute_routes`)
- `rating` - Average user rating (1.0-5.0)
- `open_now` - Whether the place is currently open

---

## get_place_details

Get comprehensive details about a specific place using its Google Place ID.

**Tool ID:** `get_place_details`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `place_id` | string | Yes | Google Place ID from `search_places` results |

### Example Request

```json
{
  "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4"
}
```

### Returns

```json
{
  "id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
  "name": "Trattoria Lisina",
  "address": "123 Congress Ave, Austin, TX 78701",
  "location": {"latitude": 30.2655, "longitude": -97.7425},
  "rating": 4.7,
  "review_count": 1842,
  "price_level": "PRICE_LEVEL_MODERATE",
  "type": "Italian restaurant",
  "types": ["italian_restaurant", "restaurant", "food", "point_of_interest"],
  "open_now": true,
  "hours": ["Monday: 11:00 AM – 10:00 PM", "..."],
  "regular_hours": ["Monday: 11:00 AM – 10:00 PM", "..."],
  "phone": "(512) 555-0123",
  "international_phone": "+1 512-555-0123",
  "website": "https://example.com",
  "google_maps_url": "https://maps.google.com/?cid=...",
  "description": "Upscale Italian eatery with handmade pasta and wine list.",
  "reviews": [
    {
      "rating": 5,
      "text": "Amazing food and great service!",
      "author": "John D.",
      "relative_time": "2 weeks ago"
    }
  ],
  "photo_count": 24
}
```

**Additional Fields vs search_places:**
- `types` - Full array of place categories
- `regular_hours` - Standard operating hours
- `international_phone` - Phone in international format
- `reviews` - Up to 5 recent reviews with ratings and text
- `photo_count` - Number of photos available

---

## compute_routes

Compute driving, walking, cycling, or transit routes between locations. Returns distance, travel time, and turn-by-turn directions.

**Tool ID:** `compute_routes`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `origin` | object | Yes | Starting location (see Location Format below) |
| `destination` | object | Yes | Ending location |
| `waypoints` | array | No | List of intermediate stops |
| `travel_mode` | string | No | Mode of transportation (default: DRIVE) |
| `routing_preference` | string | No | Traffic routing option (default: TRAFFIC_AWARE) |
| `avoid_tolls` | bool | No | Avoid toll roads (default: false) |
| `avoid_highways` | bool | No | Avoid highways (default: false) |
| `avoid_ferries` | bool | No | Avoid ferries (default: false) |
| `optimize_waypoint_order` | bool | No | Optimize waypoint order for efficiency (default: false) |
| `departure_time` | string | No | Departure time in RFC3339 format |
| `arrival_time` | string | No | Desired arrival time (primarily for TRANSIT) |
| `units` | string | No | Unit system: METRIC or IMPERIAL (default: METRIC) |
| `alternatives` | bool | No | Return alternative routes (default: false) |

### Location Format

Locations can be specified in three ways:

**Coordinates:**
```json
{"latitude": 30.2672, "longitude": -97.7431}
```

**Place ID (from search_places):**
```json
{"place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4"}
```

**Address:**
```json
{"address": "123 Main St, Austin, TX"}
```

### travel_mode Values

| Value | Description |
|-------|-------------|
| `DRIVE` | Car/automobile (default) |
| `WALK` | Walking/pedestrian |
| `BICYCLE` | Cycling |
| `TWO_WHEELER` | Motorcycle/scooter |
| `TRANSIT` | Public transportation |

### routing_preference Values

| Value | Description |
|-------|-------------|
| `TRAFFIC_UNAWARE` | Fastest route ignoring traffic |
| `TRAFFIC_AWARE` | Considers current traffic (default) |
| `TRAFFIC_AWARE_OPTIMAL` | Best quality traffic routing (slower response) |

**Note:** `routing_preference` pairs with `departure_time` for accurate traffic predictions.

### units Values

| Value | Description |
|-------|-------------|
| `METRIC` | Kilometers (default) |
| `IMPERIAL` | Miles |

**Tip:** Infer units from location context - use IMPERIAL for US locations, METRIC for most other countries.

### Example Requests

**Simple route:**
```json
{
  "origin": {"address": "Austin, TX"},
  "destination": {"address": "Houston, TX"},
  "travel_mode": "DRIVE",
  "units": "IMPERIAL"
}
```

**Route with waypoints:**
```json
{
  "origin": {"address": "Austin, TX"},
  "destination": {"address": "Houston, TX"},
  "waypoints": [
    {"address": "San Marcos, TX"},
    {"address": "San Antonio, TX"}
  ],
  "optimize_waypoint_order": true,
  "units": "IMPERIAL"
}
```

**Walking directions:**
```json
{
  "origin": {"latitude": 40.7580, "longitude": -73.9855},
  "destination": {"place_id": "ChIJaXQRs6lZwokRY6EFpJnhNNE"},
  "travel_mode": "WALK",
  "units": "IMPERIAL"
}
```

**Traffic-aware with departure time:**
```json
{
  "origin": {"address": "123 Congress Ave, Austin, TX"},
  "destination": {"address": "Austin-Bergstrom Airport"},
  "travel_mode": "DRIVE",
  "routing_preference": "TRAFFIC_AWARE",
  "departure_time": "2026-01-25T18:00:00Z",
  "avoid_tolls": true
}
```

**Transit with arrival time:**
```json
{
  "origin": {"address": "Brooklyn, NY"},
  "destination": {"address": "Manhattan, NY"},
  "travel_mode": "TRANSIT",
  "arrival_time": "2026-01-25T09:00:00-05:00"
}
```

### Returns

```json
{
  "routes": [
    {
      "distance": 165.2,
      "distance_unit": "miles",
      "duration_seconds": 9360,
      "duration": "2h 36m",
      "duration_in_traffic_seconds": 10800,
      "duration_in_traffic": "3h 0m",
      "description": "I-35 S",
      "warnings": [],
      "legs": [
        {
          "distance": 82.5,
          "distance_unit": "miles",
          "duration_seconds": 4680,
          "duration": "1h 18m",
          "start_location": {"latitude": 30.2672, "longitude": -97.7431},
          "end_location": {"latitude": 29.4241, "longitude": -98.4936}
        },
        {
          "distance": 82.7,
          "distance_unit": "miles",
          "duration_seconds": 4680,
          "duration": "1h 18m",
          "start_location": {"latitude": 29.4241, "longitude": -98.4936},
          "end_location": {"latitude": 29.7604, "longitude": -95.3698}
        }
      ],
      "optimized_waypoint_order": [1, 0],
      "polyline": "ipkcFfichVnP@j@BLoAv@aA..."
    }
  ],
  "count": 1,
  "travel_mode": "DRIVE",
  "units": "IMPERIAL"
}
```

**Key Fields:**
- `duration` - Human-readable travel time (e.g., "2h 36m")
- `duration_seconds` - Travel time in seconds for calculations
- `duration_in_traffic` - Estimated time with current traffic
- `legs` - Breakdown for each segment when using waypoints
- `optimized_waypoint_order` - Optimal order if `optimize_waypoint_order` was true
- `polyline` - Encoded route for map visualization

---

## Agent Configuration

### Adding Tools to Agent

When creating or updating an agent, include the Google Maps tools:

```json
{
  "agent_name": "Trip Planner",
  "prompt": "You are a helpful trip planning assistant. Help users find places to visit, restaurants to eat at, and plan routes between locations.",
  "tools": [
    "search_places",
    "get_place_details",
    "compute_routes",
    "get_time"
  ]
}
```

### Recommended Tool Combinations

| Use Case | Recommended Tools |
|----------|-------------------|
| Place discovery only | `search_places`, `get_place_details` |
| Navigation/directions | `search_places`, `compute_routes` |
| Full trip planning | All three tools + `get_time` for timezone awareness |

---

## Common Agent Workflows

### Finding and Comparing Restaurants

```
User: "Find Italian restaurants near downtown Austin with good ratings"

1. Agent calls: search_places(
     text_query="Italian restaurants in downtown Austin",
     min_rating=4.0,
     max_results=5
   )

2. Agent presents options with ratings, prices, and descriptions

3. User: "Tell me more about the first one"

4. Agent calls: get_place_details(place_id="ChIJ...")

5. Agent provides hours, reviews, and contact info
```

### Planning a Day Trip

```
User: "Plan a route from Austin to San Antonio with a stop for coffee"

1. Agent calls: search_places(text_query="Austin, TX")
   → Gets Austin coordinates

2. Agent calls: search_places(
     text_query="coffee shops",
     latitude=29.88,
     longitude=-97.94,
     min_rating=4.5
   )
   → Finds coffee shops between Austin and San Antonio

3. Agent calls: compute_routes(
     origin={"address": "Austin, TX"},
     destination={"address": "San Antonio, TX"},
     waypoints=[{"place_id": "coffee-shop-place-id"}],
     units="IMPERIAL"
   )

4. Agent provides total travel time and route details
```

### Getting Travel Time Estimates

```
User: "How long will it take to drive from my hotel to the airport tomorrow at 6am?"

1. Agent calls: compute_routes(
     origin={"address": "Hilton Austin"},
     destination={"address": "Austin-Bergstrom Airport"},
     travel_mode="DRIVE",
     routing_preference="TRAFFIC_AWARE",
     departure_time="2026-01-26T06:00:00-06:00",
     units="IMPERIAL"
   )

2. Agent: "The drive from Hilton Austin to Austin-Bergstrom Airport 
   will take approximately 25 minutes (12 miles) at 6am tomorrow."
```

---

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `GOOGLE_MAPS_API_KEY not set` | Missing environment variable | Add the API key to environment |
| `Google Places API error: 403` | API not enabled or key restricted | Enable APIs and check key restrictions |
| `Google Places API error: 400` | Invalid request parameters | Check parameter formats |
| `No routes found` | Invalid locations or impossible route | Verify addresses/coordinates |
| `ZERO_RESULTS` | No places match the query | Try broader search terms |

---

## Pricing Reference

Google Maps Platform uses pay-as-you-go pricing with $200/month free credit:

| API | Approximate Cost |
|-----|------------------|
| Places Text Search | ~$32 per 1,000 requests |
| Place Details | ~$17-25 per 1,000 requests |
| Routes (directions) | ~$5-10 per 1,000 routes |

For personal assistant usage, the free tier typically covers thousands of requests per month.

---

## Related Documentation

- [Utility Tools](./utility-tools.md) - get_time and think tools
- [Google Calendar Integration](./google-calendar-integration.md) - Calendar tools for scheduling
- [Gmail Integration](./gmail-integration.md) - Email tools
- [Additional Agent Tools](./additional-agent-tools.md) - Tool configuration reference

