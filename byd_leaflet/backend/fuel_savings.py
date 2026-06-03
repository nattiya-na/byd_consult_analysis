"""Fuel cost savings calculator using Thai market prices."""

PETROL_PRICE_THB_PER_L = 40.0
DIESEL_PRICE_THB_PER_L = 33.0
ELECTRICITY_PRICE_THB_PER_KWH = 4.0  # home charging average

ICE_PETROL_KM_PER_L = 12.0
ICE_DIESEL_KM_PER_L = 14.0
BEV_KM_PER_KWH = 6.0


def annual_km(daily_km: float) -> float:
    return daily_km * 365


def ice_annual_cost(daily_km: float, fuel_type: str = "petrol") -> float:
    km = annual_km(daily_km)
    if fuel_type == "diesel":
        return (km / ICE_DIESEL_KM_PER_L) * DIESEL_PRICE_THB_PER_L
    return (km / ICE_PETROL_KM_PER_L) * PETROL_PRICE_THB_PER_L


def bev_annual_cost(daily_km: float) -> float:
    km = annual_km(daily_km)
    return (km / BEV_KM_PER_KWH) * ELECTRICITY_PRICE_THB_PER_KWH


def phev_annual_cost(daily_km: float, ev_range_km: float, fuel_type: str = "petrol") -> float:
    """PHEV cost: electric for EV-range portion, fuel for the rest."""
    km = annual_km(daily_km)
    ev_fraction = min(ev_range_km / max(daily_km, 1), 1.0)
    ev_km = km * ev_fraction
    fuel_km = km * (1 - ev_fraction)

    ev_cost = (ev_km / BEV_KM_PER_KWH) * ELECTRICITY_PRICE_THB_PER_KWH
    if fuel_type == "diesel":
        fuel_cost = (fuel_km / ICE_DIESEL_KM_PER_L) * DIESEL_PRICE_THB_PER_L
    else:
        fuel_cost = (fuel_km / ICE_PETROL_KM_PER_L) * PETROL_PRICE_THB_PER_L
    return ev_cost + fuel_cost


def co2_saved_kg(daily_km: float, savings_thb: float) -> float:
    """Rough CO2 saving: petrol emits ~2.3 kg CO2/L."""
    ice_liters_per_year = annual_km(daily_km) / ICE_PETROL_KM_PER_L
    ice_co2 = ice_liters_per_year * 2.3
    bev_co2 = annual_km(daily_km) * 0.05  # Thai grid ~0.5 kgCO2/kWh ÷ 10 km/kWh proxy
    return max(ice_co2 - bev_co2, 0)


def calculate_savings(daily_km: float, model: dict, fuel_type: str = "petrol") -> dict:
    ice_cost = ice_annual_cost(daily_km, fuel_type)

    if model["type"] == "BEV":
        ev_cost = bev_annual_cost(daily_km)
    else:
        ev_range = model.get("ev_range_km", 80)
        ev_cost = phev_annual_cost(daily_km, ev_range, fuel_type)

    savings = ice_cost - ev_cost
    co2 = co2_saved_kg(daily_km, savings)

    return {
        "ice_annual_cost_thb": round(ice_cost),
        "ev_annual_cost_thb": round(ev_cost),
        "annual_savings_thb": round(savings),
        "co2_saved_kg": round(co2),
        "daily_savings_thb": round(savings / 365, 1),
        "fuel_type": fuel_type,
    }
