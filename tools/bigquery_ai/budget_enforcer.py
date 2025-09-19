#!/usr/bin/env python3
"""
Budget Enforcement System for BigQuery AI processing
Provides robust daily budget limit enforcement with multiple enforcement levels
"""
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import config, cost_config
from billing_service import get_billing_service
from query_cost_tracker import get_query_cost_tracker

console = Console()

class EnforcementLevel(Enum):
    """Budget enforcement levels"""
    NONE = "none"
    MONITORING = "monitoring"
    WARNING = "warning"
    THROTTLING = "throttling"
    BLOCKING = "blocking"
    EMERGENCY = "emergency"

class EnforcementAction(Enum):
    """Budget enforcement actions"""
    ALLOW = "allow"
    WARN = "warn"
    THROTTLE = "throttle"
    BLOCK = "block"
    EMERGENCY_STOP = "emergency_stop"

@dataclass
class BudgetRule:
    """Individual budget rule configuration"""
    rule_id: str
    name: str
    description: str
    budget_type: str  # daily, weekly, monthly, per_query
    amount_usd: float
    enforcement_level: EnforcementLevel
    actions: List[EnforcementAction]
    warning_threshold: float  # percentage
    critical_threshold: float  # percentage
    enabled: bool
    created_at: str
    updated_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        # Convert enums to strings for JSON serialization
        data['enforcement_level'] = self.enforcement_level.value
        data['actions'] = [action.value for action in self.actions]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BudgetRule':
        """Create from dictionary"""
        # Convert string back to enum
        data['enforcement_level'] = EnforcementLevel(data['enforcement_level'])
        data['actions'] = [EnforcementAction(action) for action in data['actions']]
        return cls(**data)

@dataclass
class BudgetViolation:
    """Record of a budget violation"""
    violation_id: str
    rule_id: str
    timestamp: str
    violation_type: str  # threshold_exceeded, limit_exceeded, emergency
    current_amount: float
    limit_amount: float
    percentage_used: float
    enforcement_action: EnforcementAction
    message: str
    resolved: bool
    resolved_at: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        data = asdict(self)
        # Convert enums to strings for JSON serialization
        data['enforcement_action'] = self.enforcement_action.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BudgetViolation':
        """Create from dictionary"""
        data['enforcement_action'] = EnforcementAction(data['enforcement_action'])
        return cls(**data)

class BudgetEnforcer:
    """Comprehensive budget enforcement system"""
    
    def __init__(self):
        self.billing_service = get_billing_service()
        self.query_tracker = get_query_cost_tracker()
        self.rules_file = "budget_rules.json"
        self.violations_file = "budget_violations.json"
        self.budget_rules: List[BudgetRule] = []
        self.budget_violations: List[BudgetViolation] = []
        self.enforcement_history: List[Dict] = []
        
        # Load existing rules and violations
        self.load_budget_rules()
        self.load_budget_violations()
        
        # Initialize default rules if none exist
        if not self.budget_rules:
            self.initialize_default_rules()
            
    def load_budget_rules(self):
        """Load budget rules from file"""
        try:
            if os.path.exists(self.rules_file):
                with open(self.rules_file, 'r') as f:
                    data = json.load(f)
                    self.budget_rules = [BudgetRule.from_dict(rule) for rule in data]
                    console.print(f"✅ Loaded {len(self.budget_rules)} budget rules")
        except Exception as e:
            console.print(f"⚠️  Warning: Could not load budget rules: {e}")
            
    def save_budget_rules(self):
        """Save budget rules to file"""
        try:
            data = [rule.to_dict() for rule in self.budget_rules]
            with open(self.rules_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            console.print(f"⚠️  Warning: Could not save budget rules: {e}")
            
    def load_budget_violations(self):
        """Load budget violations from file"""
        try:
            if os.path.exists(self.violations_file):
                with open(self.violations_file, 'r') as f:
                    data = json.load(f)
                    self.budget_violations = [BudgetViolation.from_dict(violation) for violation in data]
                    console.print(f"✅ Loaded {len(self.budget_violations)} budget violations")
        except Exception as e:
            console.print(f"⚠️  Warning: Could not load budget violations: {e}")
            
    def save_budget_violations(self):
        """Save budget violations to file"""
        try:
            data = [violation.to_dict() for violation in self.budget_violations]
            with open(self.violations_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            console.print(f"⚠️  Warning: Could not save budget violations: {e}")
            
    def initialize_default_rules(self):
        """Initialize default budget rules"""
        default_rules = [
            BudgetRule(
                rule_id="daily_budget_limit",
                name="Daily Budget Limit",
                description="Enforce daily spending limit for BigQuery AI processing",
                budget_type="daily",
                amount_usd=config.daily_budget_limit_usd,
                enforcement_level=EnforcementLevel.BLOCKING,
                actions=[EnforcementAction.WARN, EnforcementAction.BLOCK],
                warning_threshold=80.0,
                critical_threshold=95.0,
                enabled=True,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            BudgetRule(
                rule_id="per_query_cost_limit",
                name="Per-Query Cost Limit",
                description="Enforce maximum cost per individual query",
                budget_type="per_query",
                amount_usd=config.max_query_cost_usd,
                enforcement_level=EnforcementLevel.BLOCKING,
                actions=[EnforcementAction.WARN, EnforcementAction.BLOCK],
                warning_threshold=80.0,
                critical_threshold=100.0,
                enabled=True,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            BudgetRule(
                rule_id="weekly_budget_limit",
                name="Weekly Budget Limit",
                description="Enforce weekly spending limit",
                budget_type="weekly",
                amount_usd=config.daily_budget_limit_usd * 7,  # 7x daily limit
                enforcement_level=EnforcementLevel.THROTTLING,
                actions=[EnforcementAction.WARN, EnforcementAction.THROTTLE],
                warning_threshold=75.0,
                critical_threshold=90.0,
                enabled=True,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            BudgetRule(
                rule_id="emergency_budget_limit",
                name="Emergency Budget Limit",
                description="Emergency stop when budget is severely exceeded",
                budget_type="daily",
                amount_usd=config.daily_budget_limit_usd * 1.5,  # 150% of daily limit
                enforcement_level=EnforcementLevel.EMERGENCY,
                actions=[EnforcementAction.EMERGENCY_STOP],
                warning_threshold=100.0,
                critical_threshold=150.0,
                enabled=True,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
        ]
        
        self.budget_rules = default_rules
        self.save_budget_rules()
        console.print("✅ Initialized default budget rules")
        
    def add_budget_rule(self, rule: BudgetRule):
        """Add a new budget rule"""
        rule.rule_id = f"rule_{int(time.time())}"
        rule.created_at = datetime.now().isoformat()
        rule.updated_at = datetime.now().isoformat()
        
        self.budget_rules.append(rule)
        self.save_budget_rules()
        console.print(f"✅ Added budget rule: {rule.name}")
        
    def update_budget_rule(self, rule_id: str, updates: Dict[str, Any]):
        """Update an existing budget rule"""
        for rule in self.budget_rules:
            if rule.rule_id == rule_id:
                for key, value in updates.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                rule.updated_at = datetime.now().isoformat()
                self.save_budget_rules()
                console.print(f"✅ Updated budget rule: {rule.name}")
                return
                
        console.print(f"❌ Budget rule not found: {rule_id}")
        
    def delete_budget_rule(self, rule_id: str):
        """Delete a budget rule"""
        self.budget_rules = [rule for rule in self.budget_rules if rule.rule_id != rule_id]
        self.save_budget_rules()
        console.print(f"✅ Deleted budget rule: {rule_id}")
        
    def get_current_budget_status(self) -> Dict[str, Any]:
        """Get current budget status for all rules"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            current_costs = {}
            
            # Get daily costs
            daily_cost = self.billing_service.get_daily_cost_breakdown(today)
            if "error" not in daily_cost:
                current_costs['daily'] = daily_cost['total_cost']
            else:
                # Fallback to query tracker
                summary = self.query_tracker.get_query_cost_summary(days=1)
                if "error" not in summary:
                    current_costs['daily'] = summary['total_cost_usd']
                else:
                    current_costs['daily'] = 0.0
                    
            # Get weekly costs
            week_start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            weekly_summary = self.query_tracker.get_query_cost_summary(days=7)
            if "error" not in weekly_summary:
                current_costs['weekly'] = weekly_summary['total_cost_usd']
            else:
                current_costs['weekly'] = current_costs['daily']  # Estimate
                
            # Calculate status for each rule
            rule_statuses = []
            for rule in self.budget_rules:
                if not rule.enabled:
                    continue
                    
                current_amount = current_costs.get(rule.budget_type, 0.0)
                percentage_used = (current_amount / rule.amount_usd * 100) if rule.amount_usd > 0 else 0
                
                # Determine enforcement level
                if percentage_used >= rule.critical_threshold:
                    enforcement_level = EnforcementLevel.EMERGENCY
                    status = "critical"
                elif percentage_used >= rule.warning_threshold:
                    enforcement_level = EnforcementLevel.WARNING
                    status = "warning"
                elif percentage_used >= 100:
                    enforcement_level = EnforcementLevel.BLOCKING
                    status = "exceeded"
                else:
                    enforcement_level = EnforcementLevel.MONITORING
                    status = "healthy"
                    
                rule_statuses.append({
                    'rule_id': rule.rule_id,
                    'name': rule.name,
                    'budget_type': rule.budget_type,
                    'current_amount': current_amount,
                    'limit_amount': rule.amount_usd,
                    'percentage_used': percentage_used,
                    'status': status,
                    'enforcement_level': enforcement_level.value,
                    'actions': [action.value for action in rule.actions]
                })
                
            return {
                'timestamp': datetime.now().isoformat(),
                'current_costs': current_costs,
                'rule_statuses': rule_statuses,
                'overall_status': self._get_overall_status(rule_statuses)
            }
            
        except Exception as e:
            console.print(f"❌ Error getting budget status: {e}")
            return {"error": str(e)}
            
    def _get_overall_status(self, rule_statuses: List[Dict]) -> str:
        """Determine overall budget status"""
        if any(status['status'] == 'critical' for status in rule_statuses):
            return "critical"
        elif any(status['status'] == 'exceeded' for status in rule_statuses):
            return "exceeded"
        elif any(status['status'] == 'warning' for status in rule_statuses):
            return "warning"
        else:
            return "healthy"
            
    def can_execute_query(self, estimated_cost_usd: float) -> Tuple[bool, str, EnforcementAction]:
        """Check if a query can be executed based on budget rules"""
        try:
            budget_status = self.get_current_budget_status()
            if "error" in budget_status:
                return False, f"Budget check failed: {budget_status['error']}", EnforcementAction.BLOCK
                
            # Check per-query cost limit
            per_query_rule = next((rule for rule in self.budget_rules 
                                  if rule.budget_type == "per_query" and rule.enabled), None)
            if per_query_rule and estimated_cost_usd > per_query_rule.amount_usd:
                return False, f"Query cost exceeds per-query limit: ${estimated_cost_usd:.4f} > ${per_query_rule.amount_usd:.2f}", EnforcementAction.BLOCK
                
            # Check daily budget limit
            daily_rule = next((rule for rule in self.budget_rules 
                             if rule.budget_type == "daily" and rule.enabled), None)
            if daily_rule:
                current_daily_cost = budget_status['current_costs'].get('daily', 0.0)
                if current_daily_cost + estimated_cost_usd > daily_rule.amount_usd:
                    return False, f"Daily budget limit would be exceeded: ${current_daily_cost:.4f} + ${estimated_cost_usd:.4f} > ${daily_rule.amount_usd:.2f}", EnforcementAction.BLOCK
                    
            # Check emergency budget limit
            emergency_rule = next((rule for rule in self.budget_rules 
                                 if rule.enforcement_level == EnforcementLevel.EMERGENCY and rule.enabled), None)
            if emergency_rule:
                current_daily_cost = budget_status['current_costs'].get('daily', 0.0)
                if current_daily_cost + estimated_cost_usd > emergency_rule.amount_usd:
                    return False, f"EMERGENCY: Budget severely exceeded! ${current_daily_cost:.4f} + ${estimated_cost_usd:.4f} > ${emergency_rule.amount_usd:.2f}", EnforcementAction.EMERGENCY_STOP
                    
            return True, "Query can be executed within budget constraints", EnforcementAction.ALLOW
            
        except Exception as e:
            console.print(f"❌ Error checking budget constraints: {e}")
            return False, f"Budget check error: {e}", EnforcementAction.BLOCK
            
    def enforce_budget_rules(self, query_cost_usd: float, query_type: str = "unknown") -> List[BudgetViolation]:
        """Enforce budget rules and return any violations"""
        violations = []
        
        try:
            budget_status = self.get_current_budget_status()
            if "error" in budget_status:
                return violations
                
            for rule_status in budget_status['rule_statuses']:
                rule = next((r for r in self.budget_rules if r.rule_id == rule_status['rule_id']), None)
                if not rule or not rule.enabled:
                    continue
                    
                # Check for violations
                if rule_status['status'] in ['warning', 'exceeded', 'critical']:
                    # Create violation record
                    violation = BudgetViolation(
                        violation_id=f"violation_{int(time.time())}_{len(violations)}",
                        rule_id=rule.rule_id,
                        timestamp=datetime.now().isoformat(),
                        violation_type=rule_status['status'],
                        current_amount=rule_status['current_amount'],
                        limit_amount=rule_status['limit_amount'],
                        percentage_used=rule_status['percentage_used'],
                        enforcement_action=self._determine_enforcement_action(rule, rule_status),
                        message=f"Budget {rule_status['status']}: {rule.name} - ${rule_status['current_amount']:.4f} / ${rule_status['limit_amount']:.2f} ({rule_status['percentage_used']:.1f}%)",
                        resolved=False,
                        resolved_at=None
                    )
                    
                    violations.append(violation)
                    self.budget_violations.append(violation)
                    
                    # Log violation
                    self._log_violation(violation, query_cost_usd, query_type)
                    
            # Save violations
            if violations:
                self.save_budget_violations()
                
        except Exception as e:
            console.print(f"❌ Error enforcing budget rules: {e}")
            
        return violations
        
    def _determine_enforcement_action(self, rule: BudgetRule, rule_status: Dict) -> EnforcementAction:
        """Determine appropriate enforcement action based on rule and status"""
        if rule_status['status'] == 'critical':
            return EnforcementAction.EMERGENCY_STOP
        elif rule_status['status'] == 'exceeded':
            return EnforcementAction.BLOCK
        elif rule_status['status'] == 'warning':
            return EnforcementAction.WARN
        else:
            return EnforcementAction.ALLOW
            
    def _log_violation(self, violation: BudgetViolation, query_cost: float, query_type: str):
        """Log budget violation with details"""
        violation_log = {
            'timestamp': violation.timestamp,
            'violation_id': violation.violation_id,
            'rule_name': next((r.name for r in self.budget_rules if r.rule_id == violation.rule_id), 'Unknown'),
            'violation_type': violation.violation_type,
            'enforcement_action': violation.enforcement_action.value,
            'current_amount': violation.current_amount,
            'limit_amount': violation.limit_amount,
            'percentage_used': violation.percentage_used,
            'triggering_query_cost': query_cost,
            'triggering_query_type': query_type,
            'message': violation.message
        }
        
        self.enforcement_history.append(violation_log)
        
        # Display violation alert
        if violation.enforcement_action == EnforcementAction.EMERGENCY_STOP:
            console.print(f"🚨 EMERGENCY BUDGET VIOLATION: {violation.message}", style="bold red")
        elif violation.enforcement_action == EnforcementAction.BLOCK:
            console.print(f"🚫 BUDGET LIMIT EXCEEDED: {violation.message}", style="bold red")
        elif violation.enforcement_action == EnforcementAction.WARN:
            console.print(f"⚠️  BUDGET WARNING: {violation.message}", style="bold yellow")
            
    def get_budget_violations(self, days: int = 30, resolved: Optional[bool] = None) -> List[BudgetViolation]:
        """Get budget violations with optional filtering"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered_violations = [
            v for v in self.budget_violations
            if datetime.fromisoformat(v.timestamp) > cutoff_date
        ]
        
        if resolved is not None:
            filtered_violations = [v for v in filtered_violations if v.resolved == resolved]
            
        return filtered_violations
        
    def resolve_violation(self, violation_id: str):
        """Mark a budget violation as resolved"""
        for violation in self.budget_violations:
            if violation.violation_id == violation_id:
                violation.resolved = True
                violation.resolved_at = datetime.now().isoformat()
                self.save_budget_violations()
                console.print(f"✅ Resolved budget violation: {violation_id}")
                return
                
        console.print(f"❌ Budget violation not found: {violation_id}")
        
    def get_enforcement_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get summary of budget enforcement activities"""
        try:
            violations = self.get_budget_violations(days=days)
            budget_status = self.get_current_budget_status()
            
            # Count violations by type
            violation_counts = {}
            for violation in violations:
                violation_type = violation.violation_type
                violation_counts[violation_type] = violation_counts.get(violation_type, 0) + 1
                
            # Count enforcement actions
            action_counts = {}
            for violation in violations:
                action = violation.enforcement_action.value
                action_counts[action] = action_counts.get(action, 0) + 1
                
            # Calculate resolution rate
            resolved_count = len([v for v in violations if v.resolved])
            resolution_rate = (resolved_count / len(violations) * 100) if violations else 0
            
            return {
                'period_days': days,
                'total_violations': len(violations),
                'resolved_violations': resolved_count,
                'unresolved_violations': len(violations) - resolved_count,
                'resolution_rate_percent': resolution_rate,
                'violation_counts': violation_counts,
                'action_counts': action_counts,
                'current_budget_status': budget_status.get('overall_status', 'unknown'),
                'active_rules': len([r for r in self.budget_rules if r.enabled]),
                'total_rules': len(self.budget_rules)
            }
            
        except Exception as e:
            console.print(f"❌ Error getting enforcement summary: {e}")
            return {"error": str(e)}
            
    def display_budget_dashboard(self):
        """Display comprehensive budget enforcement dashboard"""
        try:
            console.print("\n💰 Budget Enforcement Dashboard")
            console.print("=" * 60)
            
            # Get current status
            budget_status = self.get_current_budget_status()
            if "error" in budget_status:
                console.print(f"❌ Error: {budget_status['error']}")
                return
                
            # Overall status
            overall_status = budget_status['overall_status']
            status_color = "red" if overall_status == "critical" else "yellow" if overall_status == "exceeded" else "green"
            
            status_text = Text()
            status_text.append(f"Overall Status: ", style="bold blue")
            status_text.append(f"{overall_status.upper()}", style=f"bold {status_color}")
            status_text.append(f"\nTimestamp: {budget_status['timestamp'][:19]}", style="bold cyan")
            
            status_panel = Panel(status_text, title="📊 Budget Status Overview", border_style=status_color)
            console.print(status_panel)
            
            # Current costs
            costs_text = Text()
            for cost_type, amount in budget_status['current_costs'].items():
                costs_text.append(f"{cost_type.title()}: ${amount:.4f}\n", style="bold green")
                
            costs_panel = Panel(costs_text, title="💰 Current Costs", border_style="blue")
            console.print(costs_panel)
            
            # Rule statuses
            if budget_status['rule_statuses']:
                rules_table = Table(title="📋 Budget Rules Status")
                rules_table.add_column("Rule", style="cyan")
                rules_table.add_column("Type", style="magenta")
                rules_table.add_column("Current", style="green")
                rules_table.add_column("Limit", style="yellow")
                rules_table.add_column("Usage %", style="blue")
                rules_table.add_column("Status", style="red")
                rules_table.add_column("Enforcement", style="bold")
                
                for rule_status in budget_status['rule_statuses']:
                    status_color = "red" if rule_status['status'] in ['critical', 'exceeded'] else "yellow" if rule_status['status'] == 'warning' else "green"
                    rules_table.add_row(
                        rule_status['name'],
                        rule_status['budget_type'],
                        f"${rule_status['current_amount']:.4f}",
                        f"${rule_status['limit_amount']:.2f}",
                        f"{rule_status['percentage_used']:.1f}%",
                        f"[bold {status_color}]{rule_status['status']}[/bold {status_color}]",
                        rule_status['enforcement_level']
                    )
                    
                console.print(rules_table)
                
            # Recent violations
            recent_violations = self.get_budget_violations(days=7)
            if recent_violations:
                console.print("\n🚨 Recent Budget Violations (Last 7 days)")
                console.print("=" * 50)
                
                violations_table = Table(title="🚨 Recent Violations")
                violations_table.add_column("Time", style="cyan")
                violations_table.add_column("Rule", style="magenta")
                violations_table.add_column("Type", style="green")
                violations_table.add_column("Action", style="yellow")
                violations_table.add_column("Status", style="blue")
                
                for violation in recent_violations[-10:]:  # Show last 10
                    rule_name = next((r.name for r in self.budget_rules if r.rule_id == violation.rule_id), 'Unknown')
                    time_str = violation.timestamp[:19]
                    status_color = "green" if violation.resolved else "red"
                    
                    violations_table.add_row(
                        time_str,
                        rule_name,
                        violation.violation_type,
                        violation.enforcement_action.value,
                        f"[bold {status_color}]{'Resolved' if violation.resolved else 'Active'}[/bold {status_color}]"
                    )
                    
                console.print(violations_table)
                
        except Exception as e:
            console.print(f"❌ Error displaying budget dashboard: {e}")
            
    def cleanup_old_violations(self, days_to_keep: int = 90):
        """Clean up old budget violations"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            original_count = len(self.budget_violations)
            
            self.budget_violations = [
                violation for violation in self.budget_violations
                if datetime.fromisoformat(violation.timestamp) > cutoff_date
            ]
            
            removed_count = original_count - len(self.budget_violations)
            if removed_count > 0:
                self.save_budget_violations()
                console.print(f"🧹 Cleaned up {removed_count} old budget violations")
                
        except Exception as e:
            console.print(f"❌ Error cleaning up old violations: {e}")

# Global budget enforcer instance
budget_enforcer = BudgetEnforcer()

def get_budget_enforcer() -> BudgetEnforcer:
    """Get global budget enforcer instance"""
    return budget_enforcer
