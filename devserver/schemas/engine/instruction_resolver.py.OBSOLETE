"""
Instruction Resolver - Resolves instruction types from instruction_types.json
"""
from typing import Dict, Any, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

class InstructionResolver:
    """
    Resolves instruction types (e.g., "manipulation.creative") to actual instruction text
    Loads from instruction_types.json
    """

    _instance: Optional['InstructionResolver'] = None
    _initialized: bool = False

    def __new__(cls) -> 'InstructionResolver':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.instruction_types: Dict[str, Dict[str, Any]] = {}
            self.schemas_path: Optional[Path] = None
            InstructionResolver._initialized = True

    def initialize(self, schemas_path: Path) -> None:
        """Initialize resolver and load instruction types"""
        self.schemas_path = schemas_path
        self._load_instruction_types()
        logger.info(f"InstructionResolver initialized: {len(self.instruction_types)} categories")

    def _load_instruction_types(self) -> None:
        """Load instruction types from instruction_types.json"""
        if not self.schemas_path:
            logger.error("InstructionResolver not initialized")
            return

        instruction_file = self.schemas_path / "instruction_types.json"
        if not instruction_file.exists():
            logger.error(f"instruction_types.json not found: {instruction_file}")
            return

        try:
            with open(instruction_file, 'r', encoding='utf-8') as f:
                self.instruction_types = json.load(f)

            # Log loaded categories
            categories = list(self.instruction_types.keys())
            logger.info(f"Loaded instruction categories: {', '.join(categories)}")

            # Log total variants
            total_variants = sum(len(variants) for variants in self.instruction_types.values())
            logger.info(f"Total instruction variants: {total_variants}")

        except Exception as e:
            logger.error(f"Error loading instruction_types.json: {e}")
            self.instruction_types = {}

    def resolve(self, instruction_type: str) -> Optional[Dict[str, Any]]:
        """
        Resolve instruction type to instruction data

        Args:
            instruction_type: String like "manipulation.creative" or "translation.standard"

        Returns:
            Dict with keys: instruction, description, parameters
            None if not found
        """
        if not instruction_type:
            logger.warning("Empty instruction_type provided")
            return None

        # Parse instruction type (format: "category.variant")
        parts = instruction_type.split('.')
        if len(parts) != 2:
            logger.error(f"Invalid instruction_type format: {instruction_type} (expected 'category.variant')")
            return None

        category, variant = parts

        # Get category
        if category not in self.instruction_types:
            logger.error(f"Instruction category not found: {category}")
            return None

        # Get variant
        variants = self.instruction_types[category]
        if variant not in variants:
            logger.error(f"Instruction variant not found: {category}.{variant}")
            logger.debug(f"Available variants for {category}: {', '.join(variants.keys())}")
            return None

        return variants[variant]

    def get_instruction_text(self, instruction_type: str) -> Optional[str]:
        """Get just the instruction text (convenience method)"""
        resolved = self.resolve(instruction_type)
        return resolved['instruction'] if resolved else None

    def get_parameters(self, instruction_type: str) -> Optional[Dict[str, Any]]:
        """Get parameters for instruction type (convenience method)"""
        resolved = self.resolve(instruction_type)
        return resolved.get('parameters', {}) if resolved else None

    def list_categories(self) -> list:
        """List all instruction categories"""
        return list(self.instruction_types.keys())

    def list_variants(self, category: str) -> list:
        """List all variants for a category"""
        if category not in self.instruction_types:
            return []
        return list(self.instruction_types[category].keys())

    def list_all_types(self) -> list:
        """List all instruction types in format 'category.variant'"""
        result = []
        for category, variants in self.instruction_types.items():
            for variant in variants.keys():
                result.append(f"{category}.{variant}")
        return sorted(result)

# Singleton instance
instruction_resolver = InstructionResolver()
