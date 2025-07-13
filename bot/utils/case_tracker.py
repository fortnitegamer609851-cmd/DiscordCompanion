import json
import os
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class CaseTracker:
    def __init__(self, data_file: str = 'data/cases.json'):
        self.data_file = data_file
        self.cases = self._load_cases()
        self.next_case_number = self._get_highest_case_number() + 1

    def _load_cases(self) -> Dict[str, Any]:
        """Load cases from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            logger.error(f'Error loading cases: {e}')
            return {}

    def _save_cases(self) -> None:
        """Save cases to JSON file"""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            with open(self.data_file, 'w') as f:
                json.dump(self.cases, f, indent=2)
        except Exception as e:
            logger.error(f'Error saving cases: {e}')

    def _get_highest_case_number(self) -> int:
        """Get the highest existing case number"""
        try:
            if not self.cases:
                return 0
            
            case_numbers = [int(case_id) for case_id in self.cases.keys() if case_id.isdigit()]
            return max(case_numbers) if case_numbers else 0
        except Exception as e:
            logger.error(f'Error getting highest case number: {e}')
            return 0

    def get_next_case_number(self) -> int:
        """Get the next available case number"""
        case_number = self.next_case_number
        self.next_case_number += 1
        return case_number

    def save_case(self, case_number: int, action: str, target_id: int, moderator_id: int, reason: str) -> None:
        """Save a moderation case"""
        try:
            case_data = {
                'case_number': case_number,
                'action': action,
                'target_id': target_id,
                'moderator_id': moderator_id,
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat(),
                'created_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
            }
            
            self.cases[str(case_number)] = case_data
            self._save_cases()
            
            logger.info(f'Case #{case_number} saved: {action} by {moderator_id} on {target_id}')
            
        except Exception as e:
            logger.error(f'Error saving case #{case_number}: {e}')

    def get_case(self, case_number: int) -> Dict[str, Any]:
        """Get a specific case by number"""
        try:
            return self.cases.get(str(case_number), {})
        except Exception as e:
            logger.error(f'Error getting case #{case_number}: {e}')
            return {}

    def get_cases_by_target(self, target_id: int) -> list:
        """Get all cases for a specific target"""
        try:
            target_cases = []
            for case_data in self.cases.values():
                if case_data.get('target_id') == target_id:
                    target_cases.append(case_data)
            
            # Sort by case number
            target_cases.sort(key=lambda x: x.get('case_number', 0))
            return target_cases
            
        except Exception as e:
            logger.error(f'Error getting cases for target {target_id}: {e}')
            return []

    def get_cases_by_moderator(self, moderator_id: int) -> list:
        """Get all cases by a specific moderator"""
        try:
            moderator_cases = []
            for case_data in self.cases.values():
                if case_data.get('moderator_id') == moderator_id:
                    moderator_cases.append(case_data)
            
            # Sort by case number
            moderator_cases.sort(key=lambda x: x.get('case_number', 0))
            return moderator_cases
            
        except Exception as e:
            logger.error(f'Error getting cases by moderator {moderator_id}: {e}')
            return []

    def get_total_cases(self) -> int:
        """Get total number of cases"""
        return len(self.cases)

    def get_cases_by_action(self, action: str) -> list:
        """Get all cases of a specific action type"""
        try:
            action_cases = []
            for case_data in self.cases.values():
                if case_data.get('action') == action:
                    action_cases.append(case_data)
            
            # Sort by case number
            action_cases.sort(key=lambda x: x.get('case_number', 0))
            return action_cases
            
        except Exception as e:
            logger.error(f'Error getting cases by action {action}: {e}')
            return []

    def delete_case(self, case_number: int) -> bool:
        """Delete a case (admin only)"""
        try:
            if str(case_number) in self.cases:
                del self.cases[str(case_number)]
                self._save_cases()
                logger.info(f'Case #{case_number} deleted')
                return True
            return False
            
        except Exception as e:
            logger.error(f'Error deleting case #{case_number}: {e}')
            return False
