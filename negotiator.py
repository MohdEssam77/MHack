from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent, Tool
from langchain_groq import ChatGroq
from langchain.tools import DuckDuckGoSearchRun
import os
llm = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768",
               api_key=os.getenv("GROQ_API_KEY"))


# --- Dummy Historical Data for Testing ---
historical_data = {
    "Supplier Saarstahl": {
        "contract_status": "Active",
        "on_time_delivery": 95.2,
        "quality_rating": 4.7,
        "pricing_history": {"steel": [105, 110, 108, 115, 112]}
    },
    "Supplier Siemens": {
        "contract_status": "Expired",
        "on_time_delivery": 88.5,
        "quality_rating": 4.2,
        "pricing_history": {"electronics": [98, 102, 100, 99, 101]}
    }
}

# --- Define Tool Functions ---


def current_pricing_vs_market_tool_fn(supplier_name: str, supply_type: str) -> str:
    supplier_data = historical_data.get(supplier_name, {})
    pricing_history = supplier_data.get(
        "pricing_history", {}).get(supply_type, [])
    search_tool = DuckDuckGoSearchRun()

    # Fetch market average price
    market_search_query = f"current market price for {supply_type}"
    market_average_result = search_tool.run(market_search_query)
    market_average = llm.invoke(
        f"Extract only the numeric price value from the following text:\n{market_average_result}. If no price is found, return 'Unknown'."
    )

    if pricing_history:
        current_pricing = pricing_history[-1]
    else:
        # Fetch supplier's current pricing if no historical data
        supplier_price_query = f"current pricing for {supply_type} from {supplier_name}"
        supplier_price_result = search_tool.run(supplier_price_query)
        current_pricing = llm.invoke(
            f"Extract only the numeric price value from the following text:\n{supplier_price_result}. If no price is found, return 'Unknown'."
        )

    return f"Current Pricing: ${current_pricing}\nMarket Average Pricing: ${market_average}"


def contract_status_tool_fn(supplier_name: str, supply_type: str) -> str:
    supplier_data = historical_data.get(supplier_name, {})
    return f"Contract Status: {supplier_data.get('contract_status', 'Unknown')} (for {supply_type})"


def supplier_performance_tool_fn(supplier_name: str, supply_type: str) -> str:
    supplier_data = historical_data.get(supplier_name, {})
    return (f"On-Time Delivery: {supplier_data.get('on_time_delivery', 'Unknown')}%\n"
            f"Quality Rating: {supplier_data.get('quality_rating', 'Unknown')} / 5\n"
            f"Supply Type: {supply_type}")


def negotiation_recommendation_tool_fn(supplier_name: str, supply_type: str) -> str:
    current_pricing_vs_market = current_pricing_vs_market_tool_fn(
        supplier_name, supply_type)
    supplier_data = historical_data.get(supplier_name, {})

    prompt = f"""
    Supplier: {supplier_name}
    Supply Type: {supply_type}

    {current_pricing_vs_market}

    Contract Status: {supplier_data.get('contract_status', 'Unknown')}
    Performance:
        - On-Time Delivery: {supplier_data.get('on_time_delivery', 'Unknown')}
        - Quality Rating: {supplier_data.get('quality_rating', 'Unknown')}

    Based on the above details, provide a negotiation strategy.
    """

    response = llm.invoke(prompt)
    return response


# --- Wrap Functions as LangChain Tools ---
tools = [
    Tool(
        name="Current Pricing vs. Market Tool",
        func=lambda query: current_pricing_vs_market_tool_fn(
            *query.split(",")),
        description="Compares the supplier's current pricing to the market average. Input should be 'supplier_name,supply_type'."
    ),
    Tool(
        name="Contract Status Tool",
        func=lambda query: contract_status_tool_fn(
            *query.split(",")),
        description="Retrieves the current contract status of the supplier."
    ),
    Tool(
        name="Supplier Performance Tool",
        func=lambda query: supplier_performance_tool_fn(
            *query.split(",")),
        description="Provides performance metrics such as on-time delivery and quality rating."
    ),
    Tool(
        name="Negotiation Recommendation Tool",
        func=lambda query: negotiation_recommendation_tool_fn(
            *query.split(",")),
        description="Offers negotiation recommendations based on supplier data."
    )
]

# --- Create a ReAct Agent ---
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- Function to Generate Supplier Dossier ---


def generate_supplier_dossier(supplier_name: str, supply_type: str) -> str:
    query = (f"Generate a negotiation dossier for {supplier_name} ({supply_type}) including: "
             "1. Supplier Name; "
             "2. Supply Type; "
             "3. Current Pricing vs. Market Average; "
             "4. Contract Status; "
             "5. Supplier Performance; "
             "6. Negotiation Recommendation.")

    response = agent_executor.invoke({"input": query})
    return response


# --- Example Usage ---
supplier_name = "Supplier Saarstahl"
supply_type = "steel"
dossier = generate_supplier_dossier(supplier_name, supply_type)
print(dossier)
