"""
AMT Advanced Airtable Intelligence Bridge - Production-ready integration with sophisticated Airtable brain.
Leverages existing AI integration, MEL coordination, Triangle Defense analysis, and cross-company coordination.
Designed for the actual AMT_Complete_Staff_Directory_v2 and associated intelligence tables.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import aiohttp
import time
from urllib.parse import urlencode

# Import staff registry types
from .staff_registry import StaffMember, TierLevel, ExpertiseArea, StaffStatus


class AirtableOperationType(Enum):
    """Types of Airtable operations for tracking and optimization."""
    READ_STAFF = "read_staff"
    UPDATE_STAFF = "update_staff"
    CREATE_ASSIGNMENT = "create_assignment"
    UPDATE_MEL_HUB = "update_mel_hub"
    TRIANGLE_ANALYSIS = "triangle_analysis"
    VISION_COORDINATION = "vision_coordination"
    AI_AGENT_SYNC = "ai_agent_sync"
    PERFORMANCE_UPDATE = "performance_update"


class StaffTier(Enum):
    """Actual Airtable Staff_Tier values."""
    TIER_1_FOUNDER = "Tier 1 (Founder)"
    TIER_2_C_SUITE = "Tier 2 (C-Suite)"
    TIER_3_DIRECTORS = "Tier 3 (Directors)"
    TIER_4_MANAGERS = "Tier 4 (Managers)"
    TIER_5_SPECIALISTS = "Tier 5 (Specialists)"
    AI_ENTITY = "AI Entity"


class AccessLevel(Enum):
    """Actual Airtable Access_Level values."""
    LEVEL_1_FOUNDER = "Level 1 (Founder Access)"
    LEVEL_2_EXECUTIVE = "Level 2 (Executive Access)"
    LEVEL_3_DEPARTMENT_HEAD = "Level 3 (Department Head Access)"
    LEVEL_4_MANAGER = "Level 4 (Manager Access)"
    LEVEL_5_STANDARD = "Level 5 (Standard Access)"
    AI_UNRESTRICTED = "AI Unrestricted"


class SecurityClearance(Enum):
    """Actual Airtable Security_Clearance values."""
    FOUNDER_LEVEL = "Founder Level"
    EXECUTIVE_CLEARANCE = "Executive Clearance"
    TRIANGLE_DEFENSE_CLEARANCE = "Triangle Defense Clearance"
    STANDARD_CLEARANCE = "Standard Clearance"
    LIMITED_ACCESS = "Limited Access"
    AI_CLEARANCE = "AI Clearance"


@dataclass
class StaffUpdate:
    """Staff update structure matching actual Airtable fields."""
    employee_id: str
    position_title: Optional[str] = None
    employment_status: Optional[str] = None
    performance_rating: Optional[str] = None
    current_assignment: Optional[str] = None
    work_location: Optional[str] = None
    special_projects: Optional[List[str]] = None
    last_updated: datetime = field(default_factory=datetime.now)
    additional_notes: Optional[str] = None


@dataclass
class MELIntegrationUpdate:
    """Update structure for MEL_Integration_Hub coordination."""
    integration_id: str
    analysis_type: str
    overall_mel_score: Optional[float] = None
    analysis_status: Optional[str] = None
    key_insights_summary: Optional[str] = None
    delivery_date: Optional[datetime] = None
    analysis_complexity: Optional[str] = None


@dataclass
class TriangleAnalysisUpdate:
    """Update structure for Triangle Influence Analysis coordination."""
    triangle_analysis_id: str
    formation_type: Optional[str] = None
    hash_position: Optional[str] = None
    field_zone: Optional[str] = None
    success_rate: Optional[float] = None
    triangle_defense_call: Optional[str] = None
    contributing_staff: Optional[List[str]] = None


@dataclass
class AIAgentSync:
    """AI Agent synchronization structure."""
    agent_name: str
    deployment_status: str
    performance_metrics: Optional[Dict[str, Any]] = None
    expertise_areas: Optional[List[str]] = None
    human_oversight: Optional[str] = None


class AirtableBridge:
    """
    Advanced Airtable Intelligence Bridge for AMT ecosystem.
    
    Integrates with the sophisticated production Airtable setup including:
    - AMT_Complete_Staff_Directory_v2 with AI integration
    - MEL_Integration_Hub for central coordination
    - Triangle Influence Analysis for defensive intelligence
    - DENAULD_VISION_HUB for strategic coordination
    - Multiple AI agent coordination tables
    - Cross-company assignment management
    """
    
    def __init__(self, config: Dict[str, str]):
        """
        Initialize Airtable bridge with production configuration.
        
        Args:
            config: Configuration dictionary with API key and base ID
        """
        self.base_id = config["base_id"]
        self.api_key = config["api_key"]
        self.base_url = "https://api.airtable.com/v0"
        
        # Table IDs from actual Airtable structure
        self.tables = {
            "staff_directory": "tblmtQeXQOmZQPnHe",  # AMT_Complete_Staff_Directory_v2
            "mel_integration_hub": "tbltiwxUbstUeey7G",  # MEL_Integration_Hub
            "triangle_analysis": "tblNvUVjYnmEU54tE",  # Triangle Influence Analysis
            "vision_hub": "tblnI6OvKKOk4Hg2n",  # DENAULD_VISION_HUB
            "ai_agents": "tblx4qFC4Ech1cuJj",  # AMT_AI_Agents
            "mission_control": "tblgVLFsyL6ml97Cm",  # ANALYZEMEATEAM_MISSION_CONTROL
            "making_mel": "tblaw9V5z2s9clQnM",  # making_mel
            "efficiency_mel": "tbl5BUDMxau67QeH5",  # efficiency_mel
            "logical_mel": "tblc9N6r2BoyZGJ98"  # logical_mel
        }
        
        # Field mappings for staff directory (actual field IDs)
        self.staff_fields = {
            "position_title": "fld7m0BU5sDUGade8",
            "department": "flde25sMCSkaKMCAT",
            "staff_tier": "fldEXKihcNUX1QMHz",
            "reports_to": "fldjJiUJVNn7qDef6",
            "access_level": "fldvwWaaYyacFGMF1",
            "primary_expertise": "fldnndi6q9UCida2j",
            "years_experience": "fldlDM0KyE3yN1SCe",
            "ai_counterpart": "fld8OdxyhpVbxlKF5",
            "contact_email": "fldENhmQ2f9ARi38l",
            "phone_number": "fldGlHLRpaMwihTBX",
            "start_date": "fldyc9HDbPZmeH1uM",
            "employment_status": "fldNufOLMqca4Uqem",
            "emergency_contact": "fldYVNvCxCrFQZLyn",
            "succession_backup": "fldggwgJEf1D9NmMa",
            "skills_certifications": "fldvnCZH73b6zHrRN",
            "company_assignment": "fldKDkpMTrBZoaeIA",
            "performance_rating": "flde0O3mPC8EtrcuT",
            "security_clearance": "fld1bg1APCmr3WMH1",
            "work_location": "fldAhi9PyvVtC9CpG",
            "special_projects": "fldXa3LxCZG8nMkVb",
            "professional_background": "fldNWunlJ8Mg091Qb",
            "additional_notes": "fldvJ4WrqGCCKvcN9",
            "last_updated": "fldaow9MTdkZVUkzw",
            "employee_id": "fldzmtzJsnC0XpeGb"
        }
        
        # HTTP session for efficient connection pooling
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Rate limiting and caching
        self.last_request_time = 0
        self.min_request_interval = 0.2  # 5 requests per second limit
        self.cache = {}
        self.cache_ttl = 300  # 5 minute cache TTL
        
        # Performance metrics
        self.metrics = {
            "requests_made": 0,
            "cache_hits": 0,
            "errors": 0,
            "avg_response_time": 0.0
        }
        
        # Logger
        self.logger = logging.getLogger("AMT.AirtableBridge")
        self.logger.setLevel(logging.INFO)
        
        self.logger.info("Advanced Airtable Bridge initialized for production AMT intelligence brain")
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _ensure_session(self):
        """Ensure HTTP session is available."""
        if self.session is None or self.session.closed:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(headers=headers, timeout=timeout)
    
    async def _rate_limit(self):
        """Implement rate limiting for Airtable API."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            await asyncio.sleep(self.min_request_interval - time_since_last)
        
        self.last_request_time = time.time()
    
    async def _make_request(self, 
                          method: str, 
                          table_id: str, 
                          record_id: Optional[str] = None,
                          data: Optional[Dict] = None,
                          params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make authenticated request to Airtable API with error handling and retries.
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            table_id: Airtable table ID
            record_id: Optional record ID for single record operations
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data from Airtable API
        """
        await self._ensure_session()
        await self._rate_limit()
        
        # Build URL
        url = f"{self.base_url}/{self.base_id}/{table_id}"
        if record_id:
            url += f"/{record_id}"
        
        if params:
            url += f"?{urlencode(params)}"
        
        start_time = time.time()
        
        try:
            self.metrics["requests_made"] += 1
            
            async with self.session.request(method, url, json=data) as response:
                response_time = time.time() - start_time
                
                # Update average response time
                total_requests = self.metrics["requests_made"]
                current_avg = self.metrics["avg_response_time"]
                self.metrics["avg_response_time"] = ((current_avg * (total_requests - 1)) + response_time) / total_requests
                
                if response.status == 200 or response.status == 201:
                    result = await response.json()
                    self.logger.debug(f"Successful {method} to {table_id}: {response.status}")
                    return result
                elif response.status == 429:
                    # Rate limited - wait and retry
                    self.logger.warning("Rate limited by Airtable API, retrying...")
                    await asyncio.sleep(1)
                    return await self._make_request(method, table_id, record_id, data, params)
                else:
                    error_text = await response.text()
                    self.logger.error(f"Airtable API error {response.status}: {error_text}")
                    self.metrics["errors"] += 1
                    raise Exception(f"Airtable API error {response.status}: {error_text}")
                    
        except Exception as e:
            self.logger.error(f"Request failed: {str(e)}")
            self.metrics["errors"] += 1
            raise
    
    async def get_staff_member(self, employee_id: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Retrieve staff member by employee ID with advanced caching.
        
        Args:
            employee_id: Employee ID to search for
            use_cache: Whether to use cached data
            
        Returns:
            Staff member record or None if not found
        """
        cache_key = f"staff_{employee_id}"
        
        # Check cache first
        if use_cache and cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                self.metrics["cache_hits"] += 1
                return cached_data
        
        # Search by employee ID using formula
        formula = f"{{Employee_ID}} = '{employee_id}'"
        params = {
            "filterByFormula": formula,
            "maxRecords": 1
        }
        
        try:
            response = await self._make_request("GET", self.tables["staff_directory"], params=params)
            
            if response.get("records"):
                staff_data = response["records"][0]
                
                # Cache the result
                self.cache[cache_key] = (staff_data, time.time())
                
                return staff_data
            else:
                self.logger.warning(f"Staff member not found: {employee_id}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error retrieving staff member {employee_id}: {str(e)}")
            return None
    
    async def get_all_staff(self, 
                           filters: Optional[Dict[str, Any]] = None,
                           use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve all staff members with optional filtering.
        
        Args:
            filters: Optional filters for staff retrieval
            use_cache: Whether to use cached data
            
        Returns:
            List of staff member records
        """
        cache_key = f"all_staff_{hash(str(filters)) if filters else 'all'}"
        
        # Check cache
        if use_cache and cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                self.metrics["cache_hits"] += 1
                return cached_data
        
        params = {}
        
        # Apply filters
        if filters:
            filter_conditions = []
            
            if "staff_tier" in filters:
                filter_conditions.append(f"{{Staff_Tier}} = '{filters['staff_tier']}'")
            
            if "department" in filters:
                filter_conditions.append(f"{{Department}} = '{filters['department']}'")
            
            if "employment_status" in filters:
                filter_conditions.append(f"{{Employment_Status}} = '{filters['employment_status']}'")
            
            if "access_level" in filters:
                filter_conditions.append(f"{{Access_Level}} = '{filters['access_level']}'")
            
            if filter_conditions:
                params["filterByFormula"] = "AND(" + ", ".join(filter_conditions) + ")"
        
        try:
            all_records = []
            offset = None
            
            while True:
                if offset:
                    params["offset"] = offset
                
                response = await self._make_request("GET", self.tables["staff_directory"], params=params)
                
                all_records.extend(response.get("records", []))
                
                offset = response.get("offset")
                if not offset:
                    break
            
            # Cache the results
            self.cache[cache_key] = (all_records, time.time())
            
            self.logger.info(f"Retrieved {len(all_records)} staff members")
            return all_records
            
        except Exception as e:
            self.logger.error(f"Error retrieving staff: {str(e)}")
            return []
    
    async def update_staff_member(self, 
                                 employee_id: str, 
                                 updates: StaffUpdate) -> bool:
        """
        Update staff member record with comprehensive field mapping.
        
        Args:
            employee_id: Employee ID to update
            updates: Staff update data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First get the record
            staff_record = await self.get_staff_member(employee_id, use_cache=False)
            if not staff_record:
                self.logger.error(f"Staff member not found for update: {employee_id}")
                return False
            
            record_id = staff_record["id"]
            
            # Build update fields using actual field IDs
            update_fields = {}
            
            if updates.position_title:
                update_fields[self.staff_fields["position_title"]] = updates.position_title
            
            if updates.employment_status:
                update_fields[self.staff_fields["employment_status"]] = updates.employment_status
            
            if updates.performance_rating:
                update_fields[self.staff_fields["performance_rating"]] = updates.performance_rating
            
            if updates.work_location:
                update_fields[self.staff_fields["work_location"]] = updates.work_location
            
            if updates.special_projects:
                update_fields[self.staff_fields["special_projects"]] = updates.special_projects
            
            if updates.additional_notes:
                update_fields[self.staff_fields["additional_notes"]] = updates.additional_notes
            
            # Always update last_updated timestamp
            update_fields[self.staff_fields["last_updated"]] = updates.last_updated.strftime("%Y-%m-%d")
            
            # Prepare request data
            request_data = {
                "fields": update_fields
            }
            
            # Make update request
            response = await self._make_request("PATCH", self.tables["staff_directory"], record_id, request_data)
            
            if response:
                self.logger.info(f"Successfully updated staff member: {employee_id}")
                
                # Invalidate relevant cache entries
                self._invalidate_staff_cache(employee_id)
                
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating staff member {employee_id}: {str(e)}")
            return False
    
    async def update_mel_integration_hub(self, integration_update: MELIntegrationUpdate) -> bool:
        """
        Update MEL Integration Hub for central coordination.
        
        Args:
            integration_update: MEL integration update data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if integration record exists
            formula = f"{{Integration_ID}} = '{integration_update.integration_id}'"
            params = {
                "filterByFormula": formula,
                "maxRecords": 1
            }
            
            response = await self._make_request("GET", self.tables["mel_integration_hub"], params=params)
            
            update_fields = {}
            
            if integration_update.analysis_type:
                update_fields["Analysis_Type"] = integration_update.analysis_type
            
            if integration_update.overall_mel_score is not None:
                update_fields["Overall_MEL_Score"] = integration_update.overall_mel_score
            
            if integration_update.analysis_status:
                update_fields["Analysis_Status"] = integration_update.analysis_status
            
            if integration_update.key_insights_summary:
                update_fields["Key_Insights_Summary"] = integration_update.key_insights_summary
            
            if integration_update.delivery_date:
                update_fields["Delivery_Date"] = integration_update.delivery_date.strftime("%Y-%m-%d")
            
            if integration_update.analysis_complexity:
                update_fields["Analysis_Complexity"] = integration_update.analysis_complexity
            
            request_data = {"fields": update_fields}
            
            if response.get("records"):
                # Update existing record
                record_id = response["records"][0]["id"]
                await self._make_request("PATCH", self.tables["mel_integration_hub"], record_id, request_data)
            else:
                # Create new record
                update_fields["Integration_ID"] = integration_update.integration_id
                await self._make_request("POST", self.tables["mel_integration_hub"], data=request_data)
            
            self.logger.info(f"Updated MEL Integration Hub: {integration_update.integration_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating MEL Integration Hub: {str(e)}")
            return False
    
    async def update_triangle_analysis(self, triangle_update: TriangleAnalysisUpdate) -> bool:
        """
        Update Triangle Influence Analysis for defensive intelligence.
        
        Args:
            triangle_update: Triangle analysis update data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            formula = f"{{Triangle_Analysis_ID}} = '{triangle_update.triangle_analysis_id}'"
            params = {
                "filterByFormula": formula,
                "maxRecords": 1
            }
            
            response = await self._make_request("GET", self.tables["triangle_analysis"], params=params)
            
            update_fields = {}
            
            if triangle_update.formation_type:
                update_fields["Formation_Type"] = triangle_update.formation_type
            
            if triangle_update.hash_position:
                update_fields["Hash_Position"] = triangle_update.hash_position
            
            if triangle_update.field_zone:
                update_fields["Field_Zone"] = triangle_update.field_zone
            
            if triangle_update.success_rate is not None:
                update_fields["Success_Rate"] = triangle_update.success_rate
            
            if triangle_update.triangle_defense_call:
                update_fields["Triangle_Defense_Call"] = triangle_update.triangle_defense_call
            
            if triangle_update.contributing_staff:
                # Link to staff records
                staff_links = await self._get_staff_record_links(triangle_update.contributing_staff)
                if staff_links:
                    update_fields["Contributing_Staff"] = staff_links
            
            request_data = {"fields": update_fields}
            
            if response.get("records"):
                record_id = response["records"][0]["id"]
                await self._make_request("PATCH", self.tables["triangle_analysis"], record_id, request_data)
            else:
                update_fields["Triangle_Analysis_ID"] = triangle_update.triangle_analysis_id
                await self._make_request("POST", self.tables["triangle_analysis"], data=request_data)
            
            self.logger.info(f"Updated Triangle Analysis: {triangle_update.triangle_analysis_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating Triangle Analysis: {str(e)}")
            return False
    
    async def sync_ai_agents(self, ai_sync: AIAgentSync) -> bool:
        """
        Synchronize AI agent status and performance metrics.
        
        Args:
            ai_sync: AI agent sync data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            formula = f"{{Agent_Name}} = '{ai_sync.agent_name}'"
            params = {
                "filterByFormula": formula,
                "maxRecords": 1
            }
            
            response = await self._make_request("GET", self.tables["ai_agents"], params=params)
            
            update_fields = {}
            
            if ai_sync.deployment_status:
                update_fields["Deployment_Status"] = ai_sync.deployment_status
            
            if ai_sync.performance_metrics:
                update_fields["Performance_Metrics"] = json.dumps(ai_sync.performance_metrics)
            
            if ai_sync.expertise_areas:
                update_fields["Expertise_Areas"] = ai_sync.expertise_areas
            
            if ai_sync.human_oversight:
                # Link to human oversight staff
                oversight_links = await self._get_staff_record_links([ai_sync.human_oversight])
                if oversight_links:
                    update_fields["Human_Oversight"] = oversight_links
            
            update_fields["Last_Updated"] = datetime.now().strftime("%Y-%m-%d")
            
            request_data = {"fields": update_fields}
            
            if response.get("records"):
                record_id = response["records"][0]["id"]
                await self._make_request("PATCH", self.tables["ai_agents"], record_id, request_data)
            else:
                update_fields["Agent_Name"] = ai_sync.agent_name
                await self._make_request("POST", self.tables["ai_agents"], data=request_data)
            
            self.logger.info(f"Synced AI agent: {ai_sync.agent_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error syncing AI agent {ai_sync.agent_name}: {str(e)}")
            return False
    
    async def create_mission_control_entry(self, 
                                         initiative_name: str,
                                         initiative_type: str,
                                         priority_level: str,
                                         resource_allocation: str,
                                         assigned_staff: List[str]) -> Optional[str]:
        """
        Create entry in Mission Control for high-level coordination.
        
        Args:
            initiative_name: Name of the initiative
            initiative_type: Type of initiative
            priority_level: Priority level
            resource_allocation: Resource allocation details
            assigned_staff: List of assigned staff member IDs
            
        Returns:
            Mission Control ID if successful, None otherwise
        """
        try:
            # Link to assigned staff
            staff_links = await self._get_staff_record_links(assigned_staff)
            
            fields = {
                "Initiative_Name": initiative_name,
                "Initiative_Type": initiative_type,
                "Priority_Level": priority_level,
                "Overall_Status": "Planning",
                "Resource_Allocation": resource_allocation,
                "Timeline_Start": datetime.now().strftime("%Y-%m-%d"),
                "Completion_Percentage": 0,
                "Key_Stakeholders": staff_links if staff_links else [],
                "Strategic_Importance": "High",
                "Next_Action_Required": "Initialize planning phase"
            }
            
            request_data = {"fields": fields}
            
            response = await self._make_request("POST", self.tables["mission_control"], data=request_data)
            
            if response:
                mission_id = response.get("id")
                self.logger.info(f"Created Mission Control entry: {mission_id}")
                return mission_id
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error creating Mission Control entry: {str(e)}")
            return None
    
    async def get_staff_assignments_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary of staff assignments and status.
        
        Returns:
            Summary of staff assignments across the ecosystem
        """
        try:
            # Get all active staff
            active_staff = await self.get_all_staff({"employment_status": "Active"})
            
            # Get mission control initiatives
            mission_response = await self._make_request("GET", self.tables["mission_control"])
            active_missions = mission_response.get("records", [])
            
            # Analyze staff distribution
            tier_distribution = {}
            department_distribution = {}
            project_load = {}
            
            for staff in active_staff:
                fields = staff.get("fields", {})
                
                # Tier distribution
                tier = fields.get("Staff_Tier", "Unknown")
                tier_distribution[tier] = tier_distribution.get(tier, 0) + 1
                
                # Department distribution
                dept = fields.get("Department", "Unknown")
                department_distribution[dept] = department_distribution.get(dept, 0) + 1
                
                # Project load analysis
                projects = fields.get("Special_Projects", [])
                employee_id = fields.get("Employee_ID", "Unknown")
                project_load[employee_id] = len(projects)
            
            # Calculate utilization metrics
            total_staff = len(active_staff)
            avg_project_load = sum(project_load.values()) / len(project_load) if project_load else 0
            
            summary = {
                "total_active_staff": total_staff,
                "tier_distribution": tier_distribution,
                "department_distribution": department_distribution,
                "average_project_load": avg_project_load,
                "active_missions": len(active_missions),
                "high_utilization_staff": [
                    emp_id for emp_id, load in project_load.items() if load > 3
                ],
                "available_capacity": [
                    emp_id for emp_id, load in project_load.items() if load < 2
                ],
                "summary_generated_at": datetime.now().isoformat()
            }
            
            self.logger.info("Generated staff assignments summary")
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating staff summary: {str(e)}")
            return {}
    
    async def _get_staff_record_links(self, employee_ids: List[str]) -> List[str]:
        """
        Get Airtable record IDs for staff members by employee IDs.
        
        Args:
            employee_ids: List of employee IDs to find
            
        Returns:
            List of Airtable record IDs
        """
        record_ids = []
        
        for emp_id in employee_ids:
            staff_record = await self.get_staff_member(emp_id)
            if staff_record:
                record_ids.append(staff_record["id"])
        
        return record_ids
    
    def _invalidate_staff_cache(self, employee_id: str):
        """Invalidate cache entries related to a staff member."""
        keys_to_remove = []
        
        for key in self.cache.keys():
            if employee_id in key or "all_staff" in key:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.cache[key]
    
    async def get_triangle_defense_specialists(self) -> List[Dict[str, Any]]:
        """Get all staff members with Triangle Defense expertise."""
        try:
            # Search for staff with Triangle Defense in Primary_Expertise
            formula = "SEARCH('Triangle Defense', {Primary_Expertise})"
            params = {
                "filterByFormula": formula
            }
            
            response = await self._make_request("GET", self.tables["staff_directory"], params=params)
            specialists = response.get("records", [])
            
            self.logger.info(f"Found {len(specialists)} Triangle Defense specialists")
            return specialists
            
        except Exception as e:
            self.logger.error(f"Error retrieving Triangle Defense specialists: {str(e)}")
            return []
    
    async def get_mel_coordination_status(self) -> Dict[str, Any]:
        """Get current M.E.L. coordination status across all analysis phases."""
        try:
            # Get MEL Integration Hub status
            hub_response = await self._make_request("GET", self.tables["mel_integration_hub"])
            hub_records = hub_response.get("records", [])
            
            # Get analysis pipeline status
            making_response = await self._make_request("GET", self.tables["making_mel"])
            making_records = making_response.get("records", [])
            
            efficiency_response = await self._make_request("GET", self.tables["efficiency_mel"])
            efficiency_records = efficiency_response.get("records", [])
            
            logical_response = await self._make_request("GET", self.tables["logical_mel"])
            logical_records = logical_response.get("records", [])
            
            status = {
                "hub_integrations": len(hub_records),
                "making_mel_records": len(making_records),
                "efficiency_mel_records": len(efficiency_records),
                "logical_mel_records": len(logical_records),
                "pipeline_health": "operational",
                "last_integration": datetime.now().isoformat()
            }
            
            # Analyze recent activity
            recent_threshold = datetime.now() - timedelta(hours=24)
            
            # Count recent records (simplified - would need to parse dates in production)
            status["recent_activity"] = {
                "new_analyses": 0,  # Would count recent records
                "completed_integrations": 0,
                "active_processing": 0
            }
            
            self.logger.info("Retrieved M.E.L. coordination status")
            return status
            
        except Exception as e:
            self.logger.error(f"Error retrieving M.E.L. status: {str(e)}")
            return {}
    
    async def batch_update_performance_ratings(self, 
                                             ratings: Dict[str, str]) -> Dict[str, bool]:
        """
        Batch update performance ratings for multiple staff members.
        
        Args:
            ratings: Dictionary mapping employee_id to performance rating
            
        Returns:
            Dictionary mapping employee_id to success status
        """
        results = {}
        
        for employee_id, rating in ratings.items():
            update = StaffUpdate(
                employee_id=employee_id,
                performance_rating=rating,
                additional_notes=f"Performance rating updated via batch process at {datetime.now()}"
            )
            
            success = await self.update_staff_member(employee_id, update)
            results[employee_id] = success
            
            # Small delay between updates to respect rate limits
            await asyncio.sleep(0.1)
        
        successful_updates = sum(1 for success in results.values() if success)
        self.logger.info(f"Batch updated {successful_updates}/{len(ratings)} performance ratings")
        
        return results
    
    async def get_bridge_metrics(self) -> Dict[str, Any]:
        """Get comprehensive bridge performance metrics."""
        return {
            "performance_metrics": self.metrics,
            "cache_status": {
                "entries": len(self.cache),
                "hit_rate": self.metrics["cache_hits"] / max(self.metrics["requests_made"], 1) * 100
            },
            "connection_status": "connected" if self.session and not self.session.closed else "disconnected",
            "last_request": self.last_request_time,
            "supported_operations": [op.value for op in AirtableOperationType]
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Airtable connection and key tables."""
        health_status = {
            "overall_status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "table_status": {},
            "api_connectivity": True,
            "issues": []
        }
        
        try:
            # Test connection to each key table
            for table_name, table_id in self.tables.items():
                try:
                    response = await self._make_request("GET", table_id, params={"maxRecords": 1})
                    health_status["table_status"][table_name] = "accessible"
                except Exception as e:
                    health_status["table_status"][table_name] = "error"
                    health_status["issues"].append(f"Table {table_name}: {str(e)}")
                    health_status["overall_status"] = "degraded"
            
            # Check if we have any errors
            if self.metrics["errors"] > 0:
                error_rate = self.metrics["errors"] / self.metrics["requests_made"] * 100
                if error_rate > 10:  # More than 10% error rate
                    health_status["overall_status"] = "degraded"
                    health_status["issues"].append(f"High error rate: {error_rate:.1f}%")
            
        except Exception as e:
            health_status["overall_status"] = "unhealthy"
            health_status["api_connectivity"] = False
            health_status["issues"].append(f"API connectivity: {str(e)}")
        
        return health_status


# Factory function for easy instantiation
async def create_airtable_bridge(config: Dict[str, str]) -> AirtableBridge:
    """
    Factory function to create and initialize an Airtable bridge.
    
    Args:
        config: Configuration dictionary with API credentials
        
    Returns:
        Initialized AirtableBridge instance
    """
    bridge = AirtableBridge(config)
    await bridge._ensure_session()
    return bridge
