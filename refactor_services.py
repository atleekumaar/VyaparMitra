import glob
import re

def refactor():
    files = glob.glob('src/api/services/*_service.py')
    for f in files:
        if 'twilio' in f or 'copilot' in f: continue
        with open(f, 'r') as file:
            content = file.read()
            
        # Add import if not present
        if 'from src.api.db import fetch_table_df' not in content:
            content = content.replace('import pandas as pd', 'import pandas as pd\nfrom src.api.db import fetch_table_df')
            
        # We need a way to map the variable name `summary_path` to the string `"sales_summary"`.
        # This is harder statically. Let's do a dynamic replacement of `pd.read_parquet(path_var)`
        # by looking up what `path_var` was defined as.
        
        # Let's write a small regex to find path definitions:
        # e.g., summary_path = self.analytics_dir / "sales" / "sales_summary.parquet"
        path_defs = re.findall(r'([a-zA-Z0-9_]+)\s*=\s*.*?\s*/\s*"[^"]*"\s*/\s*"([^"]+)\.parquet"', content)
        path_defs += re.findall(r'([a-zA-Z0-9_]+)\s*=\s*.*?\s*/\s*"([^"]+)\.parquet"', content)
        
        path_to_table = {}
        for var_name, table_name in path_defs:
            path_to_table[var_name] = table_name
            
        # Replace if path.exists(): with if True:
        # Wait, if we replace the if block, we can just replace var_name.exists() with True
        
        for var_name, table_name in path_to_table.items():
            content = content.replace(f'pd.read_parquet({var_name})', f'fetch_table_df("{table_name}")')
            # Also replace path.exists() inline (like in recommendation_service)
            content = content.replace(f'{var_name}.exists()', 'True')
            
        with open(f, 'w') as file:
            file.write(content)
        print(f"Refactored {f}")

if __name__ == '__main__':
    refactor()
