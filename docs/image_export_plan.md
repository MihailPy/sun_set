# Export data in image

MVP image export:

1. Load layout settings from JSON.
2. Render sunset data onto white background or template.
3. Save PNG.
4. Add tests.
5. Add GUI button later.

For image export we need

- city.name
- city.sunset_data.year
- city.sunset_data.months
- city.sunset_data.months[].month
- city.sunset_data.months[].days[].day
- city.sunset_data.months[].days[].weekday
- city.sunset_data.months[].days[].time
