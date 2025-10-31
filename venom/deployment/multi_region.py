"""
Multi-Region Deployment System
Deploy VENOM across multiple geographic regions with failover and routing
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import math

logger = logging.getLogger(__name__)

@dataclass
class Region:
    """Region configuration with geographic and infrastructure data"""
    region_id: str
    name: str
    lat: float
    lon: float
    edge_nodes: List[str]
    status: str = "active"  # active, degraded, offline

class MultiRegionManager:
    """
    Multi-Region Deployment Manager
    Manages deployments across geographic regions with failover and intelligent routing
    """
    
    # Geographic calculation constants
    EARTH_RADIUS_KM = 6371
    
    def __init__(self):
        self.regions: Dict[str, Region] = {}
        self.deployments: Dict[str, str] = {}  # deployment_id -> region_id
        logger.info("MultiRegionManager initialized")
    
    def register_region(self, region: Region) -> bool:
        """
        Register a new region for deployment
        
        Args:
            region: Region configuration to register
            
        Returns:
            True if registration successful, False otherwise
        """
        if region.region_id in self.regions:
            logger.warning(f"Region {region.region_id} already registered")
            return False
        
        self.regions[region.region_id] = region
        logger.info(f"Registered region {region.region_id} ({region.name}) at ({region.lat}, {region.lon})")
        return True
    
    def cross_region_deploy(self, deployment_id: str, source_region_id: str, target_region_id: str) -> bool:
        """
        Deploy an instance from source region to target region
        
        Args:
            deployment_id: Unique identifier for the deployment
            source_region_id: Source region ID
            target_region_id: Target region ID
            
        Returns:
            True if deployment successful, False otherwise
        """
        if source_region_id not in self.regions:
            logger.error(f"Source region {source_region_id} not found")
            return False
        
        if target_region_id not in self.regions:
            logger.error(f"Target region {target_region_id} not found")
            return False
        
        target_region = self.regions[target_region_id]
        if target_region.status == "offline":
            logger.error(f"Target region {target_region_id} is offline")
            return False
        
        # Record deployment
        self.deployments[deployment_id] = target_region_id
        logger.info(f"Deployed {deployment_id} from {source_region_id} to {target_region_id}")
        return True
    
    def region_failover(self, failed_region_id: str) -> Optional[str]:
        """
        Handle region failover by finding the nearest active region
        
        Args:
            failed_region_id: Region that has failed
            
        Returns:
            Region ID of failover target, or None if no suitable region found
        """
        if failed_region_id not in self.regions:
            logger.error(f"Failed region {failed_region_id} not found")
            return None
        
        failed_region = self.regions[failed_region_id]
        failed_region.status = "offline"
        
        # Find nearest active region
        min_distance = float('inf')
        failover_region_id = None
        
        for region_id, region in self.regions.items():
            if region_id == failed_region_id or region.status != "active":
                continue
            
            distance = self._haversine_distance(
                failed_region.lat, failed_region.lon,
                region.lat, region.lon
            )
            
            if distance < min_distance:
                min_distance = distance
                failover_region_id = region_id
        
        if failover_region_id:
            logger.info(f"Failover from {failed_region_id} to {failover_region_id}")
        else:
            logger.error(f"No suitable failover region found for {failed_region_id}")
        
        return failover_region_id
    
    def latency_based_routing(self, client_lat: float, client_lon: float) -> Optional[str]:
        """
        Route client to nearest active region based on geographic location
        
        Args:
            client_lat: Client latitude
            client_lon: Client longitude
            
        Returns:
            Region ID of nearest active region, or None if no active regions
        """
        min_distance = float('inf')
        nearest_region_id = None
        
        for region_id, region in self.regions.items():
            if region.status != "active":
                continue
            
            distance = self._haversine_distance(
                client_lat, client_lon,
                region.lat, region.lon
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest_region_id = region_id
        
        if nearest_region_id:
            logger.info(f"Routed client at ({client_lat}, {client_lon}) to region {nearest_region_id}")
        else:
            logger.warning("No active regions available for routing")
        
        return nearest_region_id
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate great-circle distance between two points on Earth
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in kilometers
        """
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        return self.EARTH_RADIUS_KM * c
    
    def get_region_status(self, region_id: str) -> Optional[str]:
        """
        Get status of a region
        
        Args:
            region_id: Region to check
            
        Returns:
            Status string or None if region not found
        """
        region = self.regions.get(region_id)
        return region.status if region else None
    
    def get_active_regions(self) -> List[str]:
        """
        Get list of all active region IDs
        
        Returns:
            List of active region IDs
        """
        return [
            region_id for region_id, region in self.regions.items()
            if region.status == "active"
        ]
    
    def get_deployment_stats(self) -> Dict[str, Any]:
        """
        Get deployment statistics across all regions
        
        Returns:
            Dict with region counts, deployment counts, and active regions
        """
        active_regions = self.get_active_regions()
        
        return {
            "total_regions": len(self.regions),
            "active_regions": len(active_regions),
            "total_deployments": len(self.deployments),
            "deployments_per_region": self._count_deployments_per_region()
        }
    
    def _count_deployments_per_region(self) -> Dict[str, int]:
        """Count deployments per region"""
        counts = {}
        for region_id in self.regions:
            counts[region_id] = sum(
                1 for dep_region in self.deployments.values()
                if dep_region == region_id
            )
        return counts
