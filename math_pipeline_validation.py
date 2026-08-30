#!/usr/bin/env python3
"""Exact RHS validation for the theorem-aware Idriç backend handoff.

The compiler artifact and backend receipt are observations of one candidate
pipeline.  This module does not elaborate source, solve obligations, or run a
backend.  It parses the two deliberately small wire formats and compares their
declared mathematical meaning with an independent exact R^128 oracle.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path
import re
from typing import Iterable, Mapping, Sequence


ONE_STEP_HEADER = "EDRIC_MATH_ONE_STEP\t1"
EXECUTION_HEADER = "MATH_BACKEND_EXECUTION\t1"
HEX_40 = re.compile(r"[0-9a-f]{40}")
HEX_64 = re.compile(r"[0-9a-f]{64}")
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_.:-]*")

VALUE_ROLES = {"vector", "covector", "sphere_point"}
TRANSFORM_KINDS = {"reflection", "plane_rotation"}
ORIENTATIONS = {"preserving", "reversing"}
OPERATIONS = {
    "Contract",
    "Dot",
    "SquaredNorm",
    "Reflect",
    "RotatePlane",
    "ActOnSphere",
}
CERTIFICATE_PROVENANCE = {
    "unification",
    "normalization",
    "structure_instance",
    "law_instance",
    "structure_law_instance",
    "named_theorem",
}
CERTIFICATE_TRACE_KEYS = {
    "registry_version",
    "goal",
    "generated_by",
    "reason",
    "resolved",
    "hypotheses",
    "conclusion",
    "resolver",
    "candidates",
    "selected_theorem",
    "generated_term",
    "core_typecheck",
    "law",
    "theorem",
    "result",
}
ABSTRACT_REALIZATIONS = {
    "scalar_loop",
    "packed_vector",
    "gpu_vector",
    "special_instruction",
}
TARGET_PLANS = {"scalar_integer", "sse2", "avx2", "pseudo_vector"}
TARGET_TO_ABSTRACT = {
    "scalar_integer": "scalar_loop",
    "sse2": "packed_vector",
    "avx2": "packed_vector",
    "pseudo_vector": "gpu_vector",
}
TEMPORARY_DISPOSITIONS = {"register", "fold", "reuse", "spill", "eliminate"}
STAGE_STATUSES = {"PASS", "FAIL", "SKIP"}


class ReceiptError(ValueError):
    """The first exact receipt boundary that failed."""


def _records(path: Path, header: str) -> list[tuple[int, list[str]]]:
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ReceiptError(f"wire_format: {path} is not UTF-8") from error
    lines = raw.splitlines()
    if not lines or lines[0] != header:
        raise ReceiptError(f"wire_format: expected header {header!r}")
    if not lines or lines[-1] != "end":
        raise ReceiptError("wire_format: receipt must end with exact 'end' row")
    parsed: list[tuple[int, list[str]]] = []
    for line_number, line in enumerate(lines[1:-1], start=2):
        if not line or line.startswith("#"):
            raise ReceiptError(
                f"wire_format:{line_number}: blank/comment rows are not permitted"
            )
        fields = line.split("\t")
        if any(field == "" for field in fields):
            raise ReceiptError(f"wire_format:{line_number}: empty field")
        parsed.append((line_number, fields))
    return parsed


def _identifier(value: str, line_number: int, label: str) -> str:
    if not IDENTIFIER.fullmatch(value):
        raise ReceiptError(f"wire_format:{line_number}: invalid {label} {value!r}")
    return value


def _positive_integer(value: str, line_number: int, label: str) -> int:
    if not value.isascii() or not value.isdecimal():
        raise ReceiptError(f"wire_format:{line_number}: {label} is not a decimal integer")
    parsed = int(value)
    if parsed <= 0:
        raise ReceiptError(f"wire_format:{line_number}: {label} must be positive")
    return parsed


def _integer(value: str, line_number: int, label: str) -> int:
    if not re.fullmatch(r"-?(0|[1-9][0-9]*)", value):
        raise ReceiptError(f"wire_format:{line_number}: {label} is not canonical integer")
    return int(value)


def _coordinates(value: str, dimension: int, line_number: int) -> tuple[int, ...]:
    fields = value.split(",")
    if len(fields) != dimension:
        raise ReceiptError(
            f"wire_format:{line_number}: expected {dimension} coordinates, got {len(fields)}"
        )
    return tuple(
        _integer(coordinate, line_number, f"coordinate[{index}]")
        for index, coordinate in enumerate(fields)
    )


def _key_values(fields: Sequence[str], line_number: int) -> dict[str, str]:
    result: dict[str, str] = {}
    for field_value in fields:
        if "=" not in field_value:
            raise ReceiptError(
                f"wire_format:{line_number}: expected key=value, got {field_value!r}"
            )
        key, value = field_value.split("=", 1)
        _identifier(key, line_number, "field key")
        if not value:
            raise ReceiptError(f"wire_format:{line_number}: empty value for {key}")
        if key in result:
            raise ReceiptError(f"wire_format:{line_number}: duplicate field {key}")
        result[key] = value
    return result


@dataclass(frozen=True)
class TypedValue:
    name: str
    role: str
    space: str
    dimension: int
    coordinates: tuple[int, ...]


@dataclass(frozen=True)
class Certificate:
    name: str
    kind: str
    provenance: str
    trace: Mapping[str, str]


@dataclass(frozen=True)
class TypedTransform:
    name: str
    kind: str
    space: str
    ambient_dimension: int
    orientation: str
    parameters: Mapping[str, str]
    certificate: str


@dataclass(frozen=True)
class MathematicalStep:
    name: str
    result: str
    operation: str
    arguments: Mapping[str, str]


@dataclass(frozen=True)
class OneStepArtifact:
    source_sha256: str
    compiler_repo: str
    compiler_head: str
    spaces: Mapping[str, int]
    values: Mapping[str, TypedValue]
    transforms: Mapping[str, TypedTransform]
    certificates: Mapping[str, Certificate]
    steps: tuple[MathematicalStep, ...]
    plan_inputs: Mapping[str, tuple[str, ...]]
    temporaries: Mapping[str, str]
    raw_sha256: str

    @classmethod
    def parse(cls, path: Path) -> "OneStepArtifact":
        records = _records(path, ONE_STEP_HEADER)
        source_digest: str | None = None
        compiler_repo: str | None = None
        compiler_head: str | None = None
        core_typecheck = False
        spaces: dict[str, int] = {}
        values: dict[str, TypedValue] = {}
        transforms: dict[str, TypedTransform] = {}
        certificates: dict[str, Certificate] = {}
        steps: list[MathematicalStep] = []
        step_names: set[str] = set()
        plan_inputs: dict[str, tuple[str, ...]] = {}
        temporaries: dict[str, str] = {}

        for line_number, fields in records:
            kind = fields[0]
            if kind == "source_sha256":
                if len(fields) != 2 or not HEX_64.fullmatch(fields[1]):
                    raise ReceiptError(
                        f"wire_format:{line_number}: malformed source_sha256"
                    )
                if source_digest is not None:
                    raise ReceiptError(f"wire_format:{line_number}: duplicate source_sha256")
                source_digest = fields[1]
            elif kind == "compiler_head":
                if len(fields) != 3 or not HEX_40.fullmatch(fields[2]):
                    raise ReceiptError(
                        f"provenance:{line_number}: malformed compiler head"
                    )
                if compiler_head is not None:
                    raise ReceiptError(
                        f"provenance:{line_number}: duplicate compiler head"
                    )
                compiler_repo = fields[1]
                compiler_head = fields[2]
            elif kind == "core_typecheck":
                if fields != ["core_typecheck", "PASS"]:
                    raise ReceiptError(
                        f"core_typecheck:{line_number}: compiler artifact is not checked"
                    )
                if core_typecheck:
                    raise ReceiptError(f"wire_format:{line_number}: duplicate core_typecheck")
                core_typecheck = True
            elif kind == "space":
                if len(fields) != 3:
                    raise ReceiptError(f"wire_format:{line_number}: malformed space row")
                name = _identifier(fields[1], line_number, "space")
                dimension = _positive_integer(fields[2], line_number, "dimension")
                if name in spaces:
                    raise ReceiptError(f"wire_format:{line_number}: duplicate space {name}")
                spaces[name] = dimension
            elif kind == "value":
                if len(fields) != 7:
                    raise ReceiptError(f"wire_format:{line_number}: malformed value row")
                name = _identifier(fields[1], line_number, "value")
                role = fields[2]
                space = _identifier(fields[3], line_number, "value space")
                dimension = _positive_integer(fields[4], line_number, "value dimension")
                if role not in VALUE_ROLES:
                    raise ReceiptError(f"wire_format:{line_number}: unknown value role {role}")
                if fields[5] != "exact_integer":
                    raise ReceiptError(
                        f"wire_format:{line_number}: only exact_integer values are accepted"
                    )
                if name in values:
                    raise ReceiptError(f"wire_format:{line_number}: duplicate value {name}")
                values[name] = TypedValue(
                    name,
                    role,
                    space,
                    dimension,
                    _coordinates(fields[6], dimension, line_number),
                )
            elif kind == "transform":
                if len(fields) < 8:
                    raise ReceiptError(f"wire_format:{line_number}: malformed transform row")
                name = _identifier(fields[1], line_number, "transform")
                transform_kind = fields[2]
                space = _identifier(fields[3], line_number, "transform space")
                ambient = _positive_integer(
                    fields[4], line_number, "transform ambient dimension"
                )
                orientation = fields[5]
                if transform_kind not in TRANSFORM_KINDS:
                    raise ReceiptError(
                        f"core_typecheck:{line_number}: unknown transform kind {transform_kind}"
                    )
                if orientation not in ORIENTATIONS:
                    raise ReceiptError(
                        f"constraint_resolution:{line_number}: unknown orientation {orientation}"
                    )
                arguments = _key_values(fields[6:], line_number)
                certificate = arguments.pop("certificate", None)
                if certificate is None:
                    raise ReceiptError(
                        f"constraint_resolution:{line_number}: transform {name} has no certificate"
                    )
                if transform_kind == "reflection":
                    if arguments != {"axis": "0"} or orientation != "reversing":
                        raise ReceiptError(
                            f"constraint_resolution:{line_number}: malformed exact reflection"
                        )
                elif transform_kind == "plane_rotation":
                    if arguments != {"i": "0", "j": "1", "turns": "1"}:
                        raise ReceiptError(
                            f"constraint_resolution:{line_number}: malformed quarter turn"
                        )
                    if orientation != "preserving":
                        raise ReceiptError(
                            f"constraint_resolution:{line_number}: quarter turn orientation error"
                        )
                if name in transforms:
                    raise ReceiptError(f"wire_format:{line_number}: duplicate transform {name}")
                transforms[name] = TypedTransform(
                    name,
                    transform_kind,
                    space,
                    ambient,
                    orientation,
                    arguments,
                    certificate,
                )
            elif kind == "certificate":
                if len(fields) < 5:
                    raise ReceiptError(f"wire_format:{line_number}: malformed certificate row")
                name = _identifier(fields[1], line_number, "certificate")
                certificate_kind = _identifier(fields[2], line_number, "certificate kind")
                if fields[3] != "PASS":
                    raise ReceiptError(
                        f"constraint_resolution:{line_number}: unsolved certificate {name}"
                    )
                provenance = fields[4]
                if provenance not in CERTIFICATE_PROVENANCE:
                    raise ReceiptError(
                        f"constraint_resolution:{line_number}: unknown provenance {provenance}"
                    )
                trace = _key_values(fields[5:], line_number)
                unknown_trace = trace.keys() - CERTIFICATE_TRACE_KEYS
                if unknown_trace:
                    unknown = ",".join(sorted(unknown_trace))
                    raise ReceiptError(
                        f"constraint_resolution:{line_number}: unknown trace fields {unknown}"
                    )
                required_trace = {
                    "goal", "generated_by", "reason", "generated_term", "core_typecheck"
                }
                missing_trace = required_trace - trace.keys()
                if missing_trace:
                    missing = ",".join(sorted(missing_trace))
                    raise ReceiptError(
                        f"constraint_resolution:{line_number}: certificate {name} "
                        f"is missing trace fields {missing}"
                    )
                if trace["core_typecheck"] != "PASS":
                    raise ReceiptError(
                        f"core_typecheck:{line_number}: generated evidence was not checked"
                    )
                if provenance == "unification" and not trace.get("resolved"):
                    raise ReceiptError(
                        f"constraint_resolution:{line_number}: unification has no resolution"
                    )
                if provenance == "named_theorem":
                    theorem_fields = {"theorem", "hypotheses", "result"}
                    missing_theorem = theorem_fields - trace.keys()
                    if missing_theorem or trace.get("result") != "solved":
                        raise ReceiptError(
                            f"constraint_resolution:{line_number}: named theorem trace "
                            "must name typed hypotheses and result=solved"
                        )
                if name in certificates:
                    raise ReceiptError(
                        f"wire_format:{line_number}: duplicate certificate {name}"
                    )
                certificates[name] = Certificate(
                    name, certificate_kind, provenance, trace
                )
            elif kind == "step":
                if len(fields) < 6:
                    raise ReceiptError(f"wire_format:{line_number}: malformed step row")
                name = _identifier(fields[1], line_number, "step")
                result = _identifier(fields[2], line_number, "step result")
                operation = fields[3]
                if operation not in OPERATIONS:
                    raise ReceiptError(
                        f"one_step_form:{line_number}: unknown operation {operation}"
                    )
                arguments = _key_values(fields[4:], line_number)
                if "certificate" not in arguments:
                    raise ReceiptError(
                        f"one_step_form:{line_number}: step {name} has no certificate"
                    )
                if name in step_names:
                    raise ReceiptError(f"wire_format:{line_number}: duplicate step {name}")
                step_names.add(name)
                steps.append(MathematicalStep(name, result, operation, arguments))
            elif kind == "plan_input":
                if len(fields) != 4 or not fields[3].startswith("certificate="):
                    raise ReceiptError(f"wire_format:{line_number}: malformed plan_input row")
                step = _identifier(fields[1], line_number, "plan step")
                plans = tuple(fields[2].split(","))
                if not plans or any(plan not in ABSTRACT_REALIZATIONS for plan in plans):
                    raise ReceiptError(f"backend_plan:{line_number}: unknown allowed plan")
                if step in plan_inputs:
                    raise ReceiptError(f"wire_format:{line_number}: duplicate plan_input {step}")
                plan_inputs[step] = plans
            elif kind == "temporary":
                if len(fields) != 3:
                    raise ReceiptError(f"wire_format:{line_number}: malformed temporary row")
                name = _identifier(fields[1], line_number, "temporary")
                disposition = fields[2]
                source_dispositions = {
                    "register_candidate",
                    "foldable",
                    "reusable",
                    "spill_permitted",
                }
                if disposition not in source_dispositions:
                    raise ReceiptError(
                        f"one_step_form:{line_number}: unknown temporary class {disposition}"
                    )
                if name in temporaries:
                    raise ReceiptError(f"wire_format:{line_number}: duplicate temporary {name}")
                temporaries[name] = disposition
            else:
                raise ReceiptError(f"wire_format:{line_number}: unknown record {kind}")

        if source_digest is None:
            raise ReceiptError("source_parse: missing source_sha256")
        if compiler_repo != "isomorphisms/Idric" or compiler_head is None:
            raise ReceiptError("provenance: missing exact isomorphisms/Idric compiler head")
        if not core_typecheck:
            raise ReceiptError("core_typecheck: missing PASS")
        for value in values.values():
            if value.space not in spaces:
                raise ReceiptError(f"core_typecheck: value {value.name} has unknown space")
            if spaces[value.space] != value.dimension:
                raise ReceiptError(
                    f"core_typecheck: value {value.name} dimension disagrees with named space"
                )
        for transform in transforms.values():
            if transform.space not in spaces:
                raise ReceiptError(
                    f"core_typecheck: transform {transform.name} has unknown space"
                )
            if spaces[transform.space] != transform.ambient_dimension:
                raise ReceiptError(
                    f"core_typecheck: transform {transform.name} ambient dimension disagrees"
                )
            if transform.certificate not in certificates:
                raise ReceiptError(
                    f"constraint_resolution: transform {transform.name} uses missing certificate"
                )
        for step in steps:
            certificate_name = step.arguments["certificate"]
            if certificate_name not in certificates:
                raise ReceiptError(
                    f"constraint_resolution: step {step.name} uses missing certificate "
                    f"{certificate_name}"
                )
            if step.name not in plan_inputs:
                raise ReceiptError(f"backend_plan: step {step.name} has no plan_input")
        raw_digest = sha256(path.read_bytes()).hexdigest()
        return cls(
            source_digest,
            compiler_repo,
            compiler_head,
            spaces,
            values,
            transforms,
            certificates,
            tuple(steps),
            plan_inputs,
            temporaries,
            raw_digest,
        )


@dataclass(frozen=True)
class ScalarObservation:
    name: str
    value: int


@dataclass(frozen=True)
class VectorObservation:
    name: str
    space: str
    coordinates: tuple[int, ...]


@dataclass(frozen=True)
class ExecutionReceipt:
    artifact_sha256: str
    compiler_repo: str
    compiler_head: str
    backend_repo: str
    backend_head: str
    target: str
    plans: Mapping[str, str]
    temporaries: Mapping[str, str]
    stages: Mapping[str, str]
    fallbacks: Mapping[str, str]
    elf_sha256: str | None
    scalars: Mapping[str, int]
    vectors: Mapping[str, VectorObservation]
    rejections: Mapping[str, tuple[str, str]]

    @classmethod
    def parse(cls, path: Path) -> "ExecutionReceipt":
        records = _records(path, EXECUTION_HEADER)
        artifact_digest: str | None = None
        compiler_repo: str | None = None
        compiler_head: str | None = None
        backend_repo: str | None = None
        backend_head: str | None = None
        target: str | None = None
        plans: dict[str, str] = {}
        temporaries: dict[str, str] = {}
        stages: dict[str, str] = {}
        fallbacks: dict[str, str] = {}
        elf_digest: str | None = None
        scalars: dict[str, int] = {}
        vectors: dict[str, VectorObservation] = {}
        rejections: dict[str, tuple[str, str]] = {}

        for line_number, fields in records:
            kind = fields[0]
            if kind == "artifact_sha256":
                if len(fields) != 2 or not HEX_64.fullmatch(fields[1]):
                    raise ReceiptError(f"wire_format:{line_number}: malformed artifact hash")
                if artifact_digest is not None:
                    raise ReceiptError(f"wire_format:{line_number}: duplicate artifact hash")
                artifact_digest = fields[1]
            elif kind == "compiler_head":
                if len(fields) != 3 or not HEX_40.fullmatch(fields[2]):
                    raise ReceiptError(f"provenance:{line_number}: malformed compiler head")
                if compiler_head is not None:
                    raise ReceiptError(f"provenance:{line_number}: duplicate compiler head")
                compiler_repo = fields[1]
                compiler_head = fields[2]
            elif kind == "backend_head":
                if len(fields) != 3 or not HEX_40.fullmatch(fields[2]):
                    raise ReceiptError(f"provenance:{line_number}: malformed backend head")
                if backend_head is not None:
                    raise ReceiptError(f"provenance:{line_number}: duplicate backend head")
                backend_repo = fields[1]
                backend_head = fields[2]
            elif kind == "target":
                if len(fields) != 2 or target is not None:
                    raise ReceiptError(f"wire_format:{line_number}: malformed target row")
                target = fields[1]
            elif kind == "plan":
                if len(fields) != 3 or fields[2] not in TARGET_PLANS:
                    raise ReceiptError(f"backend_plan:{line_number}: malformed plan row")
                step = _identifier(fields[1], line_number, "planned step")
                if step in plans:
                    raise ReceiptError(f"backend_plan:{line_number}: duplicate plan {step}")
                plans[step] = fields[2]
            elif kind == "temporary":
                if len(fields) != 4 or fields[2] not in TEMPORARY_DISPOSITIONS:
                    raise ReceiptError(f"backend_plan:{line_number}: malformed temporary row")
                name = _identifier(fields[1], line_number, "temporary")
                if name in temporaries:
                    raise ReceiptError(f"backend_plan:{line_number}: duplicate temporary {name}")
                temporaries[name] = fields[2]
            elif kind == "stage":
                if len(fields) != 4 or fields[2] not in STAGE_STATUSES:
                    raise ReceiptError(f"stages:{line_number}: malformed stage row")
                name = _identifier(fields[1], line_number, "stage")
                if name in stages:
                    raise ReceiptError(f"stages:{line_number}: duplicate stage {name}")
                stages[name] = fields[2]
            elif kind == "fallback":
                if len(fields) != 3 or fields[2] != "ABSENT":
                    raise ReceiptError(
                        f"target_codegen:{line_number}: forbidden fallback {fields[1]}"
                    )
                if fields[1] in fallbacks:
                    raise ReceiptError(f"wire_format:{line_number}: duplicate fallback row")
                fallbacks[fields[1]] = fields[2]
            elif kind == "elf_sha256":
                if len(fields) != 2 or not HEX_64.fullmatch(fields[1]):
                    raise ReceiptError(f"target_codegen:{line_number}: malformed ELF hash")
                if elf_digest is not None:
                    raise ReceiptError(f"target_codegen:{line_number}: duplicate ELF hash")
                elf_digest = fields[1]
            elif kind == "observation" and len(fields) == 5 and fields[1] == "scalar":
                _, _, name, number_type, value = fields
                if number_type != "exact_integer":
                    raise ReceiptError(
                        f"target_execution:{line_number}: scalar is not exact_integer"
                    )
                name = _identifier(name, line_number, "scalar observation")
                if name in scalars:
                    raise ReceiptError(f"wire_format:{line_number}: duplicate scalar {name}")
                scalars[name] = _integer(value, line_number, name)
            elif kind == "observation" and len(fields) == 7 and fields[1] == "vector":
                _, _, name, space, dimension_text, number_type, coordinate_text = fields
                if number_type != "exact_integer":
                    raise ReceiptError(
                        f"target_execution:{line_number}: vector is not exact_integer"
                    )
                name = _identifier(name, line_number, "vector observation")
                space = _identifier(space, line_number, "observation space")
                dimension = _positive_integer(
                    dimension_text, line_number, "observation dimension"
                )
                if name in vectors:
                    raise ReceiptError(f"wire_format:{line_number}: duplicate vector {name}")
                vectors[name] = VectorObservation(
                    name,
                    space,
                    _coordinates(coordinate_text, dimension, line_number),
                )
            elif kind == "rejection":
                if len(fields) != 4:
                    raise ReceiptError(f"wire_format:{line_number}: malformed rejection row")
                case = _identifier(fields[1], line_number, "rejection case")
                stage = _identifier(fields[2], line_number, "rejection stage")
                code = _identifier(fields[3], line_number, "rejection code")
                if case in rejections:
                    raise ReceiptError(f"wire_format:{line_number}: duplicate rejection {case}")
                rejections[case] = (stage, code)
            else:
                raise ReceiptError(f"wire_format:{line_number}: unknown/malformed record {kind}")

        if artifact_digest is None:
            raise ReceiptError("provenance: missing artifact_sha256")
        if compiler_repo != "isomorphisms/Idric" or compiler_head is None:
            raise ReceiptError("provenance: missing exact compiler head")
        if backend_repo is None or backend_head is None:
            raise ReceiptError("provenance: missing exact backend head")
        if target is None:
            raise ReceiptError("backend_plan: missing target")
        return cls(
            artifact_digest,
            compiler_repo,
            compiler_head,
            backend_repo,
            backend_head,
            target,
            plans,
            temporaries,
            stages,
            fallbacks,
            elf_digest,
            scalars,
            vectors,
            rejections,
        )


def _r128(*, first: int = 0, second: int = 0, third: int = 0, last: int = 0) -> tuple[int, ...]:
    return (first, second, third) + (0,) * 124 + (last,)


X = _r128(first=3, second=4, third=12, last=9)
Y = _r128(first=5, second=-2, third=7, last=11)
HX = _r128(first=-3, second=4, third=12, last=9)
HY = _r128(first=-5, second=-2, third=7, last=11)
GX = _r128(first=-4, second=3, third=12, last=9)
GY = _r128(first=2, second=5, third=7, last=11)
G2X = _r128(first=-3, second=-4, third=12, last=9)
G3X = _r128(first=4, second=-3, third=12, last=9)
SPHERE_BASIS = (0,) * 127 + (1,)

EXPECTED_SCALARS = {
    "contraction": 190,
    "x_dot_x": 250,
    "x_dot_y": 190,
    "x_squared_norm": 250,
    "hx_dot_hy": 190,
    "gx_dot_gy": 190,
    "sphere_squared_norm": 1,
}

EXPECTED_VECTORS = {
    "hx": HX,
    "hy": HY,
    "h2x": X,
    "gx": GX,
    "gy": GY,
    "g2x": G2X,
    "g3x": G3X,
    "g4x": X,
    "sphere_after": SPHERE_BASIS,
}

EXPECTED_REJECTIONS = {
    "vector_vector_contraction": ("constraint_generation", "E_COVECTOR_REQUIRED"),
    "mismatched_named_spaces": ("constraint_resolution", "E_NAMED_SPACE_MISMATCH"),
    "mismatched_dimensions": ("constraint_resolution", "E_DIMENSION_MISMATCH"),
    "theorem_absent": ("constraint_resolution", "E_THEOREM_ABSENT"),
    "theorem_ambiguous": ("constraint_resolution", "E_THEOREM_AMBIGUOUS"),
    "theorem_hypothesis_unsatisfied":
        ("constraint_resolution", "E_HYPOTHESIS_UNSATISFIED"),
    "orientation_error": ("constraint_resolution", "E_ORIENTATION"),
    "sphere_ambient_dimension": ("constraint_resolution", "E_SPHERE_AMBIENT"),
    "malformed_backend_operation": ("backend_plan", "E_BACKEND_OPERATION"),
    "pseudo_isa_opcode_type_mismatch":
        ("host_semantic_execution", "E_OPCODE_TYPE"),
    "forbidden_target_fallback": ("target_codegen", "E_FALLBACK"),
    "plan_changed_meaning": ("rhs_validation", "E_MEANING_CHANGED"),
}

# The same-input boundary is deliberately exact.  A backend cannot substitute
# another workload containing the same operation names or a convenient set of
# precomputed constants and still obtain an RHS PASS.
EXPECTED_STEPS = (
    ("contract", "contraction", "Contract",
     {"space": "R128", "covector": "phi", "vector": "x"}),
    ("dot_xx", "x_dot_x", "Dot",
     {"space": "R128", "left": "x", "right": "x"}),
    ("dot_xy", "x_dot_y", "Dot",
     {"space": "R128", "left": "x", "right": "y"}),
    ("norm_x", "x_squared_norm", "SquaredNorm",
     {"space": "R128", "vector": "x"}),
    ("reflect_x", "hx", "Reflect",
     {"space": "R128", "axis": "0", "vector": "x"}),
    ("reflect_y", "hy", "Reflect",
     {"space": "R128", "axis": "0", "vector": "y"}),
    ("reflect_hx", "h2x", "Reflect",
     {"space": "R128", "axis": "0", "vector": "hx"}),
    ("dot_hx_hy", "hx_dot_hy", "Dot",
     {"space": "R128", "left": "hx", "right": "hy"}),
    ("rotate_x", "gx", "RotatePlane",
     {"space": "R128", "ambient": "128", "i": "0", "j": "1",
      "turns": "1", "vector": "x"}),
    ("rotate_y", "gy", "RotatePlane",
     {"space": "R128", "ambient": "128", "i": "0", "j": "1",
      "turns": "1", "vector": "y"}),
    ("rotate_gx", "g2x", "RotatePlane",
     {"space": "R128", "ambient": "128", "i": "0", "j": "1",
      "turns": "1", "vector": "gx"}),
    ("rotate_g2x", "g3x", "RotatePlane",
     {"space": "R128", "ambient": "128", "i": "0", "j": "1",
      "turns": "1", "vector": "g2x"}),
    ("rotate_g3x", "g4x", "RotatePlane",
     {"space": "R128", "ambient": "128", "i": "0", "j": "1",
      "turns": "1", "vector": "g3x"}),
    ("dot_gx_gy", "gx_dot_gy", "Dot",
     {"space": "R128", "left": "gx", "right": "gy"}),
    ("act_sphere", "sphere_after", "ActOnSphere",
     {"sphere_dimension": "127", "ambient": "128", "space": "R128",
      "transform": "G", "point": "sphere_basis"}),
    ("sphere_norm", "sphere_squared_norm", "SquaredNorm",
     {"space": "R128", "vector": "sphere_after"}),
)


def _require_value(
    values: Mapping[str, TypedValue],
    name: str,
    role: str,
    expected: tuple[int, ...],
) -> None:
    value = values.get(name)
    if value is None:
        raise ReceiptError(f"one_step_form: missing typed value {name}")
    if value.role != role:
        raise ReceiptError(
            f"core_typecheck: {name} must be {role}, receipt says {value.role}"
        )
    if value.space != "R128" or value.dimension != 128:
        raise ReceiptError(f"core_typecheck: {name} must inhabit named space R128")
    if value.coordinates != expected:
        raise ReceiptError(f"one_step_form: {name} does not match hostile R128 fixture")


def validate_r128_pipeline(
    artifact: OneStepArtifact, receipt: ExecutionReceipt
) -> None:
    """Validate exact meaning preservation without becoming another compiler."""

    if receipt.artifact_sha256 != artifact.raw_sha256:
        raise ReceiptError("provenance: backend receipt does not bind the checked artifact")
    if (
        receipt.compiler_repo != artifact.compiler_repo
        or receipt.compiler_head != artifact.compiler_head
    ):
        raise ReceiptError("provenance: backend receipt changed the compiler head")
    if artifact.spaces.get("R128") != 128:
        raise ReceiptError("core_typecheck: missing named ambient space R128")

    _require_value(artifact.values, "x", "vector", X)
    _require_value(artifact.values, "phi", "covector", Y)
    _require_value(artifact.values, "y", "vector", Y)
    _require_value(artifact.values, "sphere_basis", "sphere_point", SPHERE_BASIS)

    if set(artifact.values) != {"x", "phi", "y", "sphere_basis"}:
        raise ReceiptError(
            "one_step_form: canonical candidate introduced non-input mathematical values"
        )

    if artifact.values["phi"].role == artifact.values["y"].role:
        raise ReceiptError("core_typecheck: covector/vector distinction was erased")

    reflection = artifact.transforms.get("H")
    rotation = artifact.transforms.get("G")
    if reflection is None or reflection.kind != "reflection":
        raise ReceiptError("one_step_form: exact reflection H was not retained")
    if reflection.orientation != "reversing":
        raise ReceiptError("constraint_resolution: reflection orientation was lost")
    if rotation is None or rotation.kind != "plane_rotation":
        raise ReceiptError("one_step_form: exact quarter-turn G was not retained")
    if rotation.orientation != "preserving":
        raise ReceiptError("constraint_resolution: quarter-turn orientation was lost")

    if set(artifact.transforms) != {"H", "G"}:
        raise ReceiptError("one_step_form: canonical transform set is not exactly H and G")

    if len(artifact.steps) != len(EXPECTED_STEPS):
        raise ReceiptError(
            f"one_step_form: expected {len(EXPECTED_STEPS)} mathematical steps, "
            f"observed {len(artifact.steps)}"
        )
    for observed, (name, result, operation, arguments) in zip(
        artifact.steps, EXPECTED_STEPS
    ):
        observed_arguments = dict(observed.arguments)
        observed_arguments.pop("certificate", None)
        if (
            observed.name != name
            or observed.result != result
            or observed.operation != operation
            or observed_arguments != arguments
        ):
            raise ReceiptError(
                f"one_step_form: step {name} changed; observed "
                f"{observed.name}/{observed.result}/{observed.operation}/"
                f"{observed_arguments}"
            )

    expected_step_names = {row[0] for row in EXPECTED_STEPS}
    if set(artifact.plan_inputs) != expected_step_names:
        raise ReceiptError("backend_plan: plan_input coverage differs from canonical steps")

    operations = {step.operation for step in artifact.steps}
    missing_operations = OPERATIONS - operations
    if missing_operations:
        names = ",".join(sorted(missing_operations))
        raise ReceiptError(f"one_step_form: mathematical operations were lost: {names}")

    for step in artifact.steps:
        selected_plan = receipt.plans.get(step.name)
        if selected_plan is None:
            raise ReceiptError(f"backend_plan: no selected plan for {step.name}")
        abstract_plan = TARGET_TO_ABSTRACT[selected_plan]
        if abstract_plan not in artifact.plan_inputs[step.name]:
            raise ReceiptError(
                f"backend_plan: {selected_plan} ({abstract_plan}) was not certified "
                f"for {step.name}"
            )

    required_common_stages = {
        "source_parse": "PASS",
        "constraint_generation": "PASS",
        "constraint_resolution": "PASS",
        "core_typecheck": "PASS",
        "one_step_form": "PASS",
        "backend_plan": "PASS",
        "target_codegen": "PASS",
    }
    for stage, expected_status in required_common_stages.items():
        if receipt.stages.get(stage) != expected_status:
            raise ReceiptError(f"{stage}: expected {expected_status}")

    if receipt.target == "x86_64-linux-direct-elf":
        if receipt.stages.get("native_execution") != "PASS":
            raise ReceiptError("native_execution: generated ELF did not run natively")
        if receipt.elf_sha256 is None:
            raise ReceiptError("target_codegen: x86 receipt has no ELF hash")
        required_fallbacks = {"RefC", "c_compiler", "assembler", "linker", "libc"}
    elif receipt.target.startswith("fragment-mock:"):
        if receipt.stages.get("hardware_execution") != "SKIP":
            raise ReceiptError("hardware_execution: fragment mock must remain SKIP")
        if receipt.stages.get("host_semantic_execution") != "PASS":
            raise ReceiptError("host_semantic_execution: host interpreter did not pass")
        if receipt.elf_sha256 is not None:
            raise ReceiptError("target_codegen: fragment mock receipt claims an ELF")
        required_fallbacks = {"glsl", "wgsl", "spirv"}
    else:
        raise ReceiptError(f"backend_plan: unsupported target {receipt.target}")

    missing_fallbacks = required_fallbacks - receipt.fallbacks.keys()
    if missing_fallbacks:
        names = ",".join(sorted(missing_fallbacks))
        raise ReceiptError(f"target_codegen: unproven fallback boundary: {names}")

    for name, expected in EXPECTED_SCALARS.items():
        observed = receipt.scalars.get(name)
        if observed != expected:
            raise ReceiptError(
                f"rhs_validation: scalar {name}: expected {expected}, observed {observed}"
            )
    for name, expected in EXPECTED_VECTORS.items():
        observed = receipt.vectors.get(name)
        if observed is None:
            raise ReceiptError(f"rhs_validation: missing vector {name}")
        if observed.space != "R128" or observed.coordinates != expected:
            raise ReceiptError(f"rhs_validation: exact vector {name} disagrees")

    if set(receipt.scalars) != set(EXPECTED_SCALARS):
        raise ReceiptError("rhs_validation: scalar observation set changed")
    if set(receipt.vectors) != set(EXPECTED_VECTORS):
        raise ReceiptError("rhs_validation: vector observation set changed")

    if artifact.values["x"].coordinates[127] == 0:
        raise ReceiptError("rhs_validation: hostile far-end coordinate was erased")

    for case, (expected_stage, expected_code) in EXPECTED_REJECTIONS.items():
        rejection = receipt.rejections.get(case)
        if rejection is None:
            raise ReceiptError(f"rhs_validation: missing hostile rejection {case}")
        observed_stage, observed_code = rejection
        if observed_stage != expected_stage or observed_code != expected_code:
            raise ReceiptError(
                f"rhs_validation: {case} failed at {observed_stage}/{observed_code}, "
                f"expected first boundary {expected_stage}/{expected_code}"
            )

    if set(receipt.rejections) != set(EXPECTED_REJECTIONS):
        raise ReceiptError("rhs_validation: hostile rejection set changed")


def validate_files(artifact_path: Path, receipt_path: Path) -> None:
    validate_r128_pipeline(
        OneStepArtifact.parse(artifact_path),
        ExecutionReceipt.parse(receipt_path),
    )


def _main(arguments: Sequence[str]) -> int:
    if len(arguments) != 3:
        raise SystemExit(
            f"usage: {arguments[0]} CHECKED_ONE_STEP_ARTIFACT BACKEND_RECEIPT"
        )
    validate_files(Path(arguments[1]), Path(arguments[2]))
    print("rhs_validation\tPASS\texact R128 mathematical meaning preserved")
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(_main(sys.argv))
