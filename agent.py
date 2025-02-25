from typing import Dict, List
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from firecrawl import FirecrawlApp
import streamlit as st

# ---------------------------------------
# 🏢 Juno Montera - Real Estate Intelligence Tool
# ---------------------------------------

class PropertyData(BaseModel):
    """Schema for property data extraction"""
    building_name: str = Field(description="Name of the building/property", alias="Building_name")
    property_type: str = Field(description="Type of property (commercial, residential, etc)", alias="Property_type")
    location_address: str = Field(description="Complete address of the property")
    price: str = Field(description="Price of the property", alias="Price")
    description: str = Field(description="Detailed description of the property", alias="Description")

class PropertiesResponse(BaseModel):
    """Schema for multiple properties response"""
    properties: List[PropertyData] = Field(description="List of property details")

class LocationData(BaseModel):
    """Schema for location price trends"""
    location: str
    price_per_sqft: float
    percent_increase: float
    rental_yield: float

class LocationsResponse(BaseModel):
    """Schema for multiple locations response"""
    locations: List[LocationData] = Field(description="List of location data points")

class FirecrawlResponse(BaseModel):
    """Schema for Firecrawl API response"""
    success: bool
    data: Dict
    status: str
    expiresAt: str

class JunoMonteraRealEstateAgent:
    """AI-powered agent for Juno Montera - Market Insights & Property Intelligence"""
    
    def __init__(self, firecrawl_api_key: str, openai_api_key: str, model_id: str = "o3-mini"):
        self.agent = Agent(
            model=OpenAIChat(id=model_id, api_key=openai_api_key),
            markdown=True,
            description="I am Juno Montera's AI-powered real estate intelligence agent, providing insights on property trends, investment opportunities, and market analysis."
        )
        self.firecrawl = FirecrawlApp(api_key=firecrawl_api_key)

    def find_properties(
        self, 
        city: str,
        max_price: float,
        property_category: str = "Residential",
        property_type: str = "Flat"
    ) -> str:
        """Find and analyze properties in Juno Montera's target markets."""
        formatted_location = city.lower()
        
        urls = [
            f"https://www.squareyards.com/sale/property-for-sale-in-{formatted_location}/*",
            f"https://www.99acres.com/property-in-{formatted_location}-ffid/*",
            f"https://housing.com/in/buy/{formatted_location}/{formatted_location}",
        ]
        
        property_type_prompt = "Flats" if property_type == "Flat" else "Individual Houses"
        
        raw_response = self.firecrawl.extract(
            urls=urls,
            params={
                'prompt': f"""Extract up to 10 different {property_category} {property_type_prompt} in {city} under {max_price} crores.
                
                Data Extraction Criteria:
                - Category: {property_category}
                - Property Type: {property_type_prompt}
                - Maximum Price: {max_price} 
                - Location: {city}
                - At least 3 and up to 10 properties
                - Include key details like name, price, location, and amenities
                
                Return the data in JSON format based on the schema.
                """,
                'schema': PropertiesResponse.model_json_schema()
            }
        )
        
        if isinstance(raw_response, dict) and raw_response.get('success'):
            properties = raw_response['data'].get('properties', [])
        else:
            properties = []

        # Generate structured real estate analysis
        analysis = self.agent.run(
            f"""Juno Montera Market Analysis - {city}
            
            Properties Data:
            {properties}

            **Analysis Requirements:**
            - Select 5-6 properties closest to {max_price} crores.
            - Highlight key features, price, and investment potential in commercial real estate.
            - Provide a structured breakdown including:
              🏢 **Selected Commercial Properties**
              💼 **Best Value Analysis for Investors**
              📍 **Location Insights for Brokers**
              💡 **Investment Recommendations for Lenders**
              🤝 **Negotiation Tips for Borrowers**
            """
        )
        
        return analysis.content

    def get_location_trends(self, city: str) -> str:
        """Retrieve price trends for key localities in the city."""
        raw_response = self.firecrawl.extract([
            f"https://www.99acres.com/property-rates-and-price-trends-in-{city.lower()}-prffid/*"
        ], {
            'prompt': """Extract price trends data for ALL major localities in the city. 
            Ensure:
            - Data for 5-10 localities.
            - Cover premium and affordable locations.
            - Format output as structured data.
            """,
            'schema': LocationsResponse.model_json_schema(),
        })
        
        if isinstance(raw_response, dict) and raw_response.get('success'):
            locations = raw_response['data'].get('locations', [])
    
            analysis = self.agent.run(
                f"""Juno Montera - Market Trends in {city}

                📊 **Summary of Location Price Trends in {city}**
                {locations}

                🏆 **Top Investment Areas in {city}**
                - Highest price appreciation
                - Best rental yields
                - Most affordable with future potential

                🎯 **Recommendations for Investors in {city}**
                - Best areas for long-term investment
                - High-demand rental locations
                - Growth corridors to watch
                """
            )
            
            return analysis.content
            
        return "No price trends data available"

def initialize_agent():
    """Initialize Juno Montera's AI Real Estate Agent"""
    if 'property_agent' not in st.session_state:
        st.session_state.property_agent = JunoMonteraRealEstateAgent(
            firecrawl_api_key=st.session_state.firecrawl_key,
            openai_api_key=st.session_state.openai_key,
            model_id=st.session_state.model_id
        )

def main():
    st.set_page_config(
        page_title="Juno Montera - Real Estate Intelligence",
        page_icon="🏢",
        layout="wide"
    )

    with st.sidebar:
        st.title("🔑 API Configuration")
        model_id = st.selectbox("Choose AI Model", ["o3-mini", "gpt-4o"])
        st.session_state.model_id = model_id

        st.subheader("🔐 API Keys")
        firecrawl_key = st.text_input("Firecrawl API Key", type="password")
        openai_key = st.text_input("OpenAI API Key", type="password")
        
        if firecrawl_key and openai_key:
            st.session_state.firecrawl_key = firecrawl_key
            st.session_state.openai_key = openai_key
            initialize_agent()

    # Add check for property_agent initialization
    if 'property_agent' not in st.session_state:
        st.warning("Please enter your API keys in the sidebar to initialize the agent.")
        return

    st.title("🏢 Juno Montera - Real Estate Intelligence")
    st.info("AI-driven insights for smarter real estate decisions.")

    # New section for blog or insights
    st.subheader("📈 Market Insights & Blog")
    st.markdown("""
    - **Latest Trends in Commercial Real Estate**
    - **Investment Opportunities in Key Markets**
    - **Expert Analysis on Property Trends**
    """)

    city = st.text_input("City", placeholder="Enter city name")
    property_category = st.selectbox("Property Category", ["Residential", "Commercial"])
    max_price = st.number_input("Max Price", min_value=0.1, max_value=100.0, value=5.0)
    property_type = st.selectbox("Property Type", ["Flat", "Individual House"])

    if st.button("🔍 Search Properties"):
        if 'property_agent' in st.session_state:  # Add safety check
            with st.spinner("Processing..."):
                result = st.session_state.property_agent.find_properties(city, max_price, property_category, property_type)
                st.markdown(result)
        else:
            st.error("Please configure API keys first")

if __name__ == "__main__":
    main()