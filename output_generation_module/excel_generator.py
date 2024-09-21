import pandas as pd

def generate_excel_report(papers, filename):
    df = pd.DataFrame(papers)
    df.to_excel(filename, index=False)
    print(f"Excel report generated: {filename}")