import asyncio
import random
import networkx as nx
from typing import Dict, List, Tuple
from fastapi import FastAPI
from pydantic import BaseModel
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import time

# --- Pydantic Data Models ---
class SystemRelationships(BaseModel):
    """Defines the input JSON structure for the DAG relationships."""
    relationships: Dict[str, List[str]]

class ComponentDetail(BaseModel):
    """Structure for a single component's health status."""
    component: str
    status: str
    details: str

class HealthReport(BaseModel):
    """The final API response structure."""
    system_status: str
    component_details: List[ComponentDetail]
    failed_components: List[str]
    graph_image_base64: str = None # Base64 encoded image for optional visualization

# --- Constants & Simulation Settings ---
# Simulate a random failure rate
FAILURE_RATE = 0.15 
# Simulated health check latency in milliseconds (for asyncio.sleep)
LATENCY_MS = 50 

# --- Core Logic Functions ---

async def check_component_health(node_id: str) -> Tuple[str, str, str | None]:
    """Simulates an asynchronous health check for a single component with random latency."""
    # Simulate I/O latency
    await asyncio.sleep(random.randint(LATENCY_MS, LATENCY_MS * 4) / 1000)
    
    # Simulate a failure based on the FAILURE_RATE
    if random.random() < FAILURE_RATE:
        status = "DOWN"
        error = "Service unreachable (Simulated Timeout)"
    else:
        status = "UP"
        error = None
        
    return node_id, status, error

def create_dag_from_json(relationships: Dict[str, List[str]]) -> nx.DiGraph:
    """Creates a Directed Acyclic Graph (DAG) using NetworkX."""
    G = nx.DiGraph()
    for parent, children in relationships.items():
        # Add edges based on relationships
        for child in children:
            G.add_edge(parent, child)
    return G

def format_table(results: List[Tuple[str, str, str]]) -> str:
    """Formats the results into a simple, readable ASCII table string."""
    header = ["Component", "Status", "Details"]
    row_format = "{:<20} {:<10} {:<30}"
    
    table = "\n" + row_format.format(*header) + "\n"
    table += "-" * 60 + "\n"
    
    for component, status, error in results:
        details = error if error else "OK"
        table += row_format.format(component, status, details) + "\n"
        
    return table

def draw_graph(G: nx.DiGraph, failed_nodes: List[str]) -> str:
    """Generates and returns a Base64 encoded image of the DAG, highlighting failed nodes."""
    
    # Set node colors based on status
    node_colors = ['red' if node in failed_nodes else '#7AC142' for node in G.nodes()] # Green for UP, Red for DOWN
    
    # Use spring_layout for an aesthetically pleasing arrangement
    pos = nx.spring_layout(G, seed=42) 
    
    plt.figure(figsize=(10, 7))
    nx.draw(G, pos, 
            with_labels=True, 
            node_size=2500, 
            node_color=node_colors, 
            font_size=12, 
            font_color='black',
            edge_color='gray', 
            arrows=True)
            
    plt.title("System Dependency Health Check")
    
    # Save image to an in-memory buffer
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close() # Close plot to free memory
    
    # Encode to Base64 for inclusion in the JSON response
    return base64.b64encode(buf.getvalue()).decode('utf-8')


# --- FastAPI Endpoint ---

app = FastAPI(
    title="DAG System Health API",
    description="Checks the health of multi-level system components.",
    version="1.0.0"
)

@app.post("/healthcheck", response_model=HealthReport)
async def perform_health_check(system_data: SystemRelationships):
    """
    Performs an asynchronous health check across all unique components 
    defined in the input DAG relationships.
    """
    start_time = time.time()
    
    # 1. Graph Creation
    G = create_dag_from_json(system_data.relationships)
    
    # 2. Identify all unique nodes 
    all_nodes = set(G.nodes())
    
    # 3. Create and Run Asynchronous Tasks (Concurrent Checks)
    # Note: Concurrent checking is far more efficient than sequential BFS traversal
    tasks = [check_component_health(node) for node in all_nodes]
    raw_results = await asyncio.gather(*tasks)
    
    # 4. Process Results and Determine System Status
    component_details = []
    failed_components = []
    system_status = "UP"
    
    for node, status, error in raw_results:
        component_details.append(ComponentDetail(
            component=node,
            status=status,
            details=error if error else "OK"
        ))
        
        if status == "DOWN":
            failed_components.append(node)
            system_status = "DOWN" 
            
    # Sort results alphabetically for consistent display
    component_details.sort(key=lambda x: x.component) 
    
    # 5. Format and Print Table (for server console)
    table_data = [(d.component, d.status, d.details) for d in component_details]
    table_output = format_table(table_data)
    
    end_time = time.time()
    elapsed = round(end_time - start_time, 2)
    
    print(f"\n--- System Health Check Complete (Time: {elapsed}s) ---")
    print(table_output)
    print("------------------------------------------------------\n")
    
    # 6. Generate Graph Image
    graph_base64 = draw_graph(G, failed_components)

    # 7. Final Report
    report = HealthReport(
        system_status=system_status,
        component_details=component_details,
        failed_components=failed_components,
        graph_image_base64=graph_base64
    )
    
    return report