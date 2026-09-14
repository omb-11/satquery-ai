import pytest
from backend.tools.spatial_focus import SpatialFocusEngine
from backend.tools.visualization_planner import VisualizationPlanner
from backend.inference.gemini import GeminiAnalyst

def test_spatial_focus_cardinal():
    engine = SpatialFocusEngine()
    
    # Northwest query
    focus_nw = engine.extract_focus("Inspect the northwest sector for flooding")
    assert len(focus_nw) > 0
    assert focus_nw[0]["bbox_norm"] == [0.0, 0.0, 0.5, 0.5]
    assert "Northwest" in focus_nw[0]["label"]
    
    # Southeast query
    focus_se = engine.extract_focus("Look at the southeast quadrant")
    assert len(focus_se) > 0
    assert focus_se[0]["bbox_norm"] == [0.5, 0.5, 1.0, 1.0]

def test_spatial_focus_features():
    engine = SpatialFocusEngine()
    # Test directional focus with cardinal keyword
    focus_center = engine.extract_focus("Analyze the center of the scene")
    assert len(focus_center) > 0
    assert focus_center[0]["bbox_norm"] == [0.25, 0.25, 0.75, 0.75]

def test_visualization_planner_single_optical():
    planner = VisualizationPlanner()
    tool_results = {
        "spectral": {
            "ndvi_stats": {"mean": 0.65, "min": 0.1, "max": 0.85},
            "ndwi_stats": {"mean": -0.25, "min": -0.5, "max": 0.3},
            "ndbi_stats": {"mean": -0.15, "min": -0.4, "max": 0.2}
        }
    }
    
    plan_dict = planner.plan(
        query="Describe vegetation health", 
        input_mode="single", 
        tool_results=tool_results,
        evidence=[],
        metadata=[{"modality": "optical"}],
        parameters={}
    )
    assert "visualizations" in plan_dict
    assert "charts" in plan_dict
    charts = plan_dict["charts"]
    assert len(charts) > 0
    assert any("Vegetation" in c["title"] for c in charts)
    
    # Check chart contents
    veg_chart = next(c for c in charts if "Vegetation" in c["title"])
    assert "data" in veg_chart
    assert len(veg_chart["data"]) > 0

def test_visualization_planner_change():
    planner = VisualizationPlanner()
    tool_results = {
        "change_detection": {
            "overall_change_pct": 14.8,
            "regions": [
                {"change_type": "surface_modification", "area_px": 820, "area_pct": 8.2},
                {"change_type": "new_built_up", "area_px": 660, "area_pct": 6.6}
            ]
        }
    }
    
    plan_dict = planner.plan(
        query="What changed between T1 and T2?", 
        input_mode="bitemporal", 
        tool_results=tool_results,
        evidence=[],
        metadata=[],
        parameters={}
    )
    assert "visualizations" in plan_dict
    assert "charts" in plan_dict
    charts = plan_dict["charts"]
    assert len(charts) > 0
    assert any("Disturbance" in c["title"] for c in charts)

@pytest.mark.asyncio
async def test_gemini_analyst_fallback():
    # Analyst without key should indicate unconfigured and safely return None so orchestrator uses local RS synthesizer
    analyst = GeminiAnalyst(api_key="")
    assert not analyst.is_configured()
    
    # Connection check
    conn = await analyst.test_connection()
    assert conn["status"] == "NOT_CONFIGURED"
    
    # Synthesis returns None when unconfigured, triggering deterministic local fallback
    briefing = await analyst.synthesize_briefing(
        query="What is the condition of the water body?",
        task_type="SINGLE_VQA",
        tool_results={"spectral": {"ndwi_stats": {"mean": 0.42}}},
        evidence=[],
        confidence_report=None,
        metadata=[],
        parameters={}
    )
    assert briefing is None


@pytest.mark.asyncio
async def test_settings_routes(client):
    # Test GET /api/v1/settings/gemini
    res = await client.get("/api/v1/settings/gemini")
    assert res.status_code == 200
    data = res.json()
    assert "configured" in data
    assert "model" in data
    
    # Test GET /api/v1/settings/precision
    res_p = await client.get("/api/v1/settings/precision")
    assert res_p.status_code == 200
    data_p = res_p.json()
    assert "precision_mode" in data_p
    assert "supported_modes" in data_p

    # Test POST /api/v1/settings/precision
    res_set_p = await client.post("/api/v1/settings/precision", json={"precision_mode": "expert"})
    assert res_set_p.status_code == 200
    assert res_set_p.json()["precision_mode"] == "expert"

