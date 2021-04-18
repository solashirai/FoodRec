from pathlib import Path

SRC_ROOT = Path(__file__).parent.parent
SPARQL_DIR = (SRC_ROOT / "food_kg_sparql_queries").resolve()
SPARQL_J2_DIR = (SPARQL_DIR / "j2").resolve()
PROJECT_ROOT = SRC_ROOT.parent
DATA_DIR = (PROJECT_ROOT / "data").resolve()
