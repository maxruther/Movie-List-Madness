import re


test_str = 'musicbox_show_info_2025-07-16_mc_info.csv'

# Prepare table name from filename

# Remove 'csv' extension
test_str = test_str.replace('.csv', '')

# Remove scrape date, if present
date_contained = re.search(r'(_\d{4}-\d{2}-\d{2})', test_str)
print(date_contained)
if date_contained:
    test_str = test_str.replace(date_contained.group(), '')

print(test_str)