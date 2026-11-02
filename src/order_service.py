import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional


class OrderService:
    """
    Mock Order Service providing customer order lookups and cancellation checks.
    Reads from data/orders.json and handles missing, delayed, or malformed data gracefully.
    """

    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        if not self.data_path.exists():
            raise FileNotFoundError(f"Orders database not found at: {data_path}")
        
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        self.reference_now = datetime.fromisoformat(
            raw_data.get("_meta", {}).get("reference_now", "2026-11-01T12:00:00Z").replace("Z", "+00:00")
        )
        # Store orders in a lookup dictionary by order_id
        self.orders: Dict[str, Dict[str, Any]] = {
            order["order_id"].upper(): order for order in raw_data.get("orders", [])
        }

    def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        Retrieves order information for a given order_id.
        Returns a clean dictionary or an error payload if not found.
        """
        clean_id = order_id.strip().upper()
        order = self.orders.get(clean_id)

        if not order:
            return {
                "success": False,
                "error": f"Order '{order_id}' was not found in our system. Please verify the order number."
            }

        # Check for malformed / pending tracking numbers (like ORD-1004)
        tracking = order.get("tracking_number")
        tracking_status = "Available" if tracking and not tracking.startswith("TRK-PENDING") else "Pending/Invalid"

        return {
            "success": True,
            "order_id": order["order_id"],
            "status": order["status"],
            "order_date": order["order_date"],
            "delivery_date": order.get("delivery_date"),
            "tracking_number": tracking,
            "tracking_status": tracking_status,
            "items": order["items"]
        }

    def check_cancellation_eligibility(self, order_id: str) -> Dict[str, Any]:
        """
        Checks whether an order can be cancelled under the 30-minute policy window.
        """
        lookup = self.get_order(order_id)
        if not lookup["success"]:
            return lookup

        order_dt = datetime.fromisoformat(lookup["order_date"].replace("Z", "+00:00"))
        minutes_elapsed = (self.reference_now - order_dt).total_seconds() / 60.0

        if minutes_elapsed <= 30.0:
            return {
                "success": True,
                "can_cancel": True,
                "minutes_elapsed": round(minutes_elapsed, 1),
                "message": f"Order {order_id} was placed {round(minutes_elapsed, 1)} minutes ago and is eligible for cancellation."
            }
        else:
            return {
                "success": True,
                "can_cancel": False,
                "minutes_elapsed": round(minutes_elapsed, 1),
                "message": f"Order {order_id} was placed {round(minutes_elapsed, 1)} minutes ago (exceeds the 30-minute cancellation window). It cannot be cancelled, but may be returned after delivery."
            }



if __name__ == "__main__":
    orders_file = r"c:\Users\Shivam\Desktop\Task\data\orders.json"
    service = OrderService(orders_file)

   
    print("Test 1 (Lookup):", service.get_order("ORD-1001"))

   
    print("\nTest 2 (Can Cancel):", service.check_cancellation_eligibility("ORD-1002"))

  
    print("\nTest 3 (Cannot Cancel):", service.check_cancellation_eligibility("ORD-1001"))

    print("\nTest 4 (Missing Order):", service.get_order("ORD-9999"))
