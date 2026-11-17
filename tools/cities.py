"""Latitude/longitude of common US freight cities, used to draw lanes on the map.

A lane city that isn't listed here can be given coordinates in content/lanes.yml
(origin_coords / destination_coords: [latitude, longitude]), or added below.
"""

CITIES = {
    "Albuquerque, NM": (35.08, -106.65), "Allentown, PA": (40.60, -75.47), "Amarillo, TX": (35.22, -101.83),
    "Atlanta, GA": (33.75, -84.39), "Augusta, GA": (33.47, -81.97), "Austin, TX": (30.27, -97.74),
    "Baltimore, MD": (39.29, -76.61), "Baton Rouge, LA": (30.45, -91.19), "Birmingham, AL": (33.52, -86.80),
    "Boise, ID": (43.62, -116.20), "Boston, MA": (42.36, -71.06), "Buffalo, NY": (42.89, -78.88),
    "Charleston, SC": (32.78, -79.93), "Charlotte, NC": (35.23, -80.84), "Chattanooga, TN": (35.05, -85.31),
    "Chicago, IL": (41.88, -87.63), "Cincinnati, OH": (39.10, -84.51), "Cleveland, OH": (41.50, -81.69),
    "Columbia, SC": (34.00, -81.03), "Columbus, GA": (32.46, -84.99), "Columbus, OH": (39.96, -83.00),
    "Dallas, TX": (32.78, -96.80), "Dalton, GA": (34.77, -84.97), "Denver, CO": (39.74, -104.99),
    "Des Moines, IA": (41.59, -93.62), "Detroit, MI": (42.33, -83.05), "El Paso, TX": (31.76, -106.49),
    "Fort Worth, TX": (32.75, -97.33), "Gainesville, GA": (34.30, -83.82), "Greensboro, NC": (36.07, -79.79),
    "Greenville, SC": (34.85, -82.40), "Gulfport, MS": (30.37, -89.09), "Harrisburg, PA": (40.27, -76.88),
    "Houston, TX": (29.76, -95.37), "Huntsville, AL": (34.73, -86.59), "Indianapolis, IN": (39.77, -86.16),
    "Jackson, MS": (32.30, -90.18), "Jacksonville, FL": (30.33, -81.66), "Kansas City, MO": (39.10, -94.58),
    "Knoxville, TN": (35.96, -83.92), "Laredo, TX": (27.51, -99.51), "Las Vegas, NV": (36.17, -115.14),
    "Lexington, KY": (38.04, -84.50), "Little Rock, AR": (34.75, -92.29), "Los Angeles, CA": (34.05, -118.24),
    "Louisville, KY": (38.25, -85.76), "Lubbock, TX": (33.58, -101.86), "Macon, GA": (32.84, -83.63),
    "Memphis, TN": (35.15, -90.05), "Miami, FL": (25.76, -80.19), "Milwaukee, WI": (43.04, -87.91),
    "Minneapolis, MN": (44.98, -93.27), "Mobile, AL": (30.69, -88.04), "Montgomery, AL": (32.37, -86.30),
    "Nashville, TN": (36.16, -86.78), "New Orleans, LA": (29.95, -90.07), "New York, NY": (40.71, -74.01),
    "Newark, NJ": (40.74, -74.17), "Norfolk, VA": (36.85, -76.29), "Oklahoma City, OK": (35.47, -97.52),
    "Omaha, NE": (41.26, -95.93), "Orlando, FL": (28.54, -81.38), "Philadelphia, PA": (39.95, -75.17),
    "Phoenix, AZ": (33.45, -112.07), "Pittsburgh, PA": (40.44, -79.99), "Portland, OR": (45.52, -122.68),
    "Raleigh, NC": (35.78, -78.64), "Richmond, VA": (37.54, -77.44), "Sacramento, CA": (38.58, -121.49),
    "Salt Lake City, UT": (40.76, -111.89), "San Antonio, TX": (29.42, -98.49), "San Diego, CA": (32.72, -117.16),
    "Savannah, GA": (32.08, -81.09), "Seattle, WA": (47.61, -122.33), "Shreveport, LA": (32.53, -93.75),
    "St. Louis, MO": (38.63, -90.20), "Tallahassee, FL": (30.44, -84.28), "Tampa, FL": (27.95, -82.46),
    "Tulsa, OK": (36.15, -95.99), "Valdosta, GA": (30.83, -83.28), "Wichita, KS": (37.69, -97.34),
}
