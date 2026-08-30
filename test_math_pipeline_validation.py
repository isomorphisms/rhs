#!/usr/bin/env python3

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

from math_pipeline_validation import ReceiptError, validate_complete_files, validate_files


def coordinates(first: int, second: int, third: int, last: int) -> str:
    return ",".join(map(str, (first, second, third) + (0,) * 124 + (last,)))


X = coordinates(3, 4, 12, 9)
Y = coordinates(5, -2, 7, 11)
HX = coordinates(-3, 4, 12, 9)
HY = coordinates(-5, -2, 7, 11)
GX = coordinates(-4, 3, 12, 9)
GY = coordinates(2, 5, 7, 11)
G2X = coordinates(-3, -4, 12, 9)
G3X = coordinates(4, -3, 12, 9)
SPHERE = ",".join(map(str, (0,) * 127 + (1,)))


def artifact_text() -> str:
    steps = [
        ("contract", "contraction", "Contract",
         ["space=R128", "covector=phi", "vector=x"], "cert_same"),
        ("dot_xx", "x_dot_x", "Dot",
         ["space=R128", "left=x", "right=x"], "cert_same"),
        ("dot_xy", "x_dot_y", "Dot",
         ["space=R128", "left=x", "right=y"], "cert_same"),
        ("norm_x", "x_squared_norm", "SquaredNorm",
         ["space=R128", "vector=x"], "cert_same"),
        ("reflect_x", "hx", "Reflect",
         ["space=R128", "axis=0", "vector=x"], "cert_H"),
        ("reflect_y", "hy", "Reflect",
         ["space=R128", "axis=0", "vector=y"], "cert_H"),
        ("reflect_hx", "h2x", "Reflect",
         ["space=R128", "axis=0", "vector=hx"], "cert_H"),
        ("dot_hx_hy", "hx_dot_hy", "Dot",
         ["space=R128", "left=hx", "right=hy"], "cert_same"),
        ("rotate_x", "gx", "RotatePlane",
         ["space=R128", "ambient=128", "i=0", "j=1", "turns=1", "vector=x"],
         "cert_G"),
        ("rotate_y", "gy", "RotatePlane",
         ["space=R128", "ambient=128", "i=0", "j=1", "turns=1", "vector=y"],
         "cert_G"),
        ("rotate_gx", "g2x", "RotatePlane",
         ["space=R128", "ambient=128", "i=0", "j=1", "turns=1", "vector=gx"],
         "cert_G"),
        ("rotate_g2x", "g3x", "RotatePlane",
         ["space=R128", "ambient=128", "i=0", "j=1", "turns=1", "vector=g2x"],
         "cert_G"),
        ("rotate_g3x", "g4x", "RotatePlane",
         ["space=R128", "ambient=128", "i=0", "j=1", "turns=1", "vector=g3x"],
         "cert_G"),
        ("dot_gx_gy", "gx_dot_gy", "Dot",
         ["space=R128", "left=gx", "right=gy"], "cert_same"),
        ("act_sphere", "sphere_after", "ActOnSphere",
         ["sphere_dimension=127", "ambient=128", "space=R128", "transform=G",
          "point=sphere_basis"], "cert_sphere"),
        ("sphere_norm", "sphere_squared_norm", "SquaredNorm",
         ["space=R128", "vector=sphere_after"], "cert_sphere"),
    ]
    rows = [
        "EDRIC_MATH_ONE_STEP\t1",
        "source_sha256\t" + "a" * 64,
        "compiler_head\tisomorphisms/Idric\t" + "d" * 40,
        "core_typecheck\tPASS",
        "space\tR128\t128",
        f"value\tx\tvector\tR128\t128\texact_integer\t{X}",
        f"value\tphi\tcovector\tR128\t128\texact_integer\t{Y}",
        f"value\ty\tvector\tR128\t128\texact_integer\t{Y}",
        f"value\tsphere_basis\tsphere_point\tR128\t128\texact_integer\t{SPHERE}",
    ]
    rows.extend(
        [
            "certificate\tcert_same\tSameSpace\tPASS\tunification\t"
            "goal=SameSpaceAndDimension_R128_128\tgenerated_by=contract\t"
            "reason=unification\tresolved=space:R128,dimension:128\t"
            "generated_term=SameNamedSpace\tcore_typecheck=PASS",
            "certificate\tcert_H\tOrthogonalTransform\tPASS\tstructure_law_instance\t"
            "goal=OrthogonalTransform_H_R128_128_reversing\tgenerated_by=reflect\t"
            "reason=structure_law_instance\tlaw=first_axis_reflection_is_orthogonal\t"
            "generated_term=FirstAxisReflection\tcore_typecheck=PASS",
            "certificate\tcert_G\tOrthogonalTransform\tPASS\tstructure_law_instance\t"
            "goal=OrthogonalTransform_G_R128_128_preserving\tgenerated_by=rotatePlane\t"
            "reason=structure_law_instance\tlaw=first_plane_quarter_turn_is_orthogonal\t"
            "generated_term=FirstPlaneQuarterTurn\tcore_typecheck=PASS",
            "certificate\tcert_sphere\tOrthogonalSphereAction\tPASS\tnamed_theorem\t"
            "goal=OrthogonalSphereAction_G_127_128\tgenerated_by=actOnSphere\t"
            "reason=named_theorem\ttheorem=orthogonal_action_preserves_unit_sphere\t"
            "hypotheses=G:OrthogonalTransform_R128_128_preserving\tresult=solved\t"
            "generated_term=orthogonal_action_preserves_unit_sphere_G\t"
            "core_typecheck=PASS",
        ]
    )
    rows.extend(
        [
            "transform\tH\treflection\tR128\t128\treversing\taxis=0\tcertificate=cert_H",
            "transform\tG\tplane_rotation\tR128\t128\tpreserving\ti=0\tj=1\tturns=1\tcertificate=cert_G",
        ]
    )
    for name, result, operation, arguments, certificate in steps:
        rows.append("\t".join(
            ["step", name, result, operation, *arguments, f"certificate={certificate}"]
        ))
        rows.append(
            f"plan_input\t{name}\tscalar_loop,gpu_vector\tcertificate={certificate}"
        )
    rows.extend(["temporary\tt0\tregister_candidate", "end"])
    return "\n".join(rows) + "\n"


REJECTIONS = {
    "vector_vector_contraction": ("constraint_generation", "E_COVECTOR_REQUIRED"),
    "mismatched_named_spaces": ("constraint_resolution", "E_NAMED_SPACE_MISMATCH"),
    "mismatched_dimensions": ("constraint_resolution", "E_DIMENSION_MISMATCH"),
    "theorem_absent": ("constraint_resolution", "E_THEOREM_ABSENT"),
    "theorem_ambiguous": ("constraint_resolution", "E_THEOREM_AMBIGUOUS"),
    "theorem_hypothesis_unsatisfied": (
        "constraint_resolution",
        "E_HYPOTHESIS_UNSATISFIED",
    ),
    "orientation_error": ("constraint_resolution", "E_ORIENTATION"),
    "sphere_ambient_dimension": ("constraint_resolution", "E_SPHERE_AMBIENT"),
    "malformed_backend_operation": ("backend_plan", "E_BACKEND_OPERATION"),
    "pseudo_isa_opcode_type_mismatch": (
        "host_semantic_execution",
        "E_OPCODE_TYPE",
    ),
    "forbidden_target_fallback": ("target_codegen", "E_FALLBACK"),
    "plan_changed_meaning": ("rhs_validation", "E_MEANING_CHANGED"),
}


def receipt_text(artifact_digest: str, *, target: str = "x86_64-linux-direct-elf") -> str:
    steps = [
        "contract", "dot_xx", "dot_xy", "norm_x", "reflect_x", "reflect_y",
        "reflect_hx", "dot_hx_hy", "rotate_x", "rotate_y", "rotate_gx",
        "rotate_g2x", "rotate_g3x", "dot_gx_gy", "act_sphere", "sphere_norm",
    ]
    rows = [
        "MATH_BACKEND_EXECUTION\t1",
        f"artifact_sha256\t{artifact_digest}",
        "compiler_head\tisomorphisms/Idric\t" + "d" * 40,
        "backend_head\tisomorphisms/backend\t" + "b" * 40,
        f"target\t{target}",
    ]
    plan = "pseudo_vector" if target.startswith("fragment-mock:") else "scalar_integer"
    rows.extend(f"plan\t{step}\t{plan}" for step in steps)
    rows.append("temporary\tt0\tregister\tkept live")
    common_stages = [
        "source_parse",
        "constraint_generation",
        "constraint_resolution",
        "core_typecheck",
        "one_step_form",
        "backend_plan",
        "target_codegen",
    ]
    rows.extend(f"stage\t{stage}\tPASS\tchecked" for stage in common_stages)
    if target.startswith("fragment-mock:"):
        rows.extend(
            [
                "stage\thardware_execution\tSKIP\tnot_applicable=fragment_mock_not_hardware",
                "stage\thost_semantic_execution\tPASS\thost interpreter",
                "fallback\tglsl\tABSENT",
                "fallback\twgsl\tABSENT",
                "fallback\tspirv\tABSENT",
            ]
        )
    else:
        rows.extend(
            [
                "stage\tnative_execution\tPASS\tdirect ELF ran",
                "fallback\tRefC\tABSENT",
                "fallback\tc_compiler\tABSENT",
                "fallback\tassembler\tABSENT",
                "fallback\tlinker\tABSENT",
                "fallback\tlibc\tABSENT",
                "elf_sha256\t" + "c" * 64,
            ]
        )
    rows.extend(
        [
            "observation\tscalar\tcontraction\texact_integer\t190",
            "observation\tscalar\tx_dot_x\texact_integer\t250",
            "observation\tscalar\tx_dot_y\texact_integer\t190",
            "observation\tscalar\tx_squared_norm\texact_integer\t250",
            "observation\tscalar\thx_dot_hy\texact_integer\t190",
            "observation\tscalar\tgx_dot_gy\texact_integer\t190",
            "observation\tscalar\tsphere_squared_norm\texact_integer\t1",
            f"observation\tvector\thx\tR128\t128\texact_integer\t{HX}",
            f"observation\tvector\thy\tR128\t128\texact_integer\t{HY}",
            f"observation\tvector\th2x\tR128\t128\texact_integer\t{X}",
            f"observation\tvector\tgx\tR128\t128\texact_integer\t{GX}",
            f"observation\tvector\tgy\tR128\t128\texact_integer\t{GY}",
            f"observation\tvector\tg2x\tR128\t128\texact_integer\t{G2X}",
            f"observation\tvector\tg3x\tR128\t128\texact_integer\t{G3X}",
            f"observation\tvector\tg4x\tR128\t128\texact_integer\t{X}",
            f"observation\tvector\tsphere_after\tR128\t128\texact_integer\t{SPHERE}",
        ]
    )
    rows.append("end")
    return "\n".join(rows) + "\n"


def write_hostile_receipts(directory: Path) -> None:
    candidate_cases = {
        "malformed_backend_operation": ("one_step_artifact", "one-step"),
        "pseudo_isa_opcode_type_mismatch": ("pseudo_isa", "pseudo-isa"),
        "forbidden_target_fallback": ("pseudo_isa", "pseudo-isa"),
    }
    common = [
        "source_parse",
        "constraint_generation",
        "constraint_resolution",
        "core_typecheck",
        "one_step_form",
        "backend_plan",
        "target_codegen",
    ]
    for case, (failed_stage, code) in REJECTIONS.items():
        if failed_stage == "rhs_validation":
            continue
        source = directory / f"hostile-{case}.idric"
        source.write_text(f"hostile source: {case}\n", encoding="utf-8")
        target = (
            "fragment-mock:mali-g57-valhall"
            if failed_stage in {"host_semantic_execution", "target_codegen"}
            and case != "malformed_backend_operation"
            else "x86_64-linux-direct-elf"
        )
        stages = common + (
            ["hardware_execution", "host_semantic_execution"]
            if target.startswith("fragment-mock:")
            else ["native_execution"]
        )
        rows = [
            "MATH_BACKEND_EXECUTION\t1",
            "artifact_sha256\t" + "e" * 64,
            f"case_source_sha256\t{sha256(source.read_bytes()).hexdigest()}",
        ]
        if case in candidate_cases:
            kind, suffix = candidate_cases[case]
            candidate = directory / f"hostile-{case}.{suffix}"
            candidate.write_text(f"rejected {kind}: {case}\n", encoding="utf-8")
            rows.extend(
                [
                    f"case_candidate_kind\t{kind}",
                    f"case_candidate_sha256\t{sha256(candidate.read_bytes()).hexdigest()}",
                ]
            )
        rows.extend(
            [
                "compiler_head\tisomorphisms/Idric\t" + "d" * 40,
                "backend_head\tisomorphisms/backend\t" + "b" * 40,
                f"target\t{target}",
            ]
        )
        failed_index = stages.index(failed_stage)
        for index, stage in enumerate(stages):
            if stage == failed_stage:
                rows.append(f"stage\t{stage}\tFAIL\tdiagnostic={code}")
            elif (
                target.startswith("fragment-mock:")
                and failed_stage == "host_semantic_execution"
                and stage == "hardware_execution"
            ):
                rows.append(
                    "stage\thardware_execution\tSKIP\t"
                    "not_applicable=fragment_mock_not_hardware"
                )
            elif index < failed_index:
                rows.append(f"stage\t{stage}\tPASS\tchecked")
            else:
                rows.append(f"stage\t{stage}\tSKIP\tblocked_by={failed_stage}")
        rows.append("end")
        (directory / f"hostile-{case}.tsv").write_text(
            "\n".join(rows) + "\n", encoding="utf-8"
        )


class MathPipelineValidationTests(unittest.TestCase):
    def write_pair(
        self, directory: Path, *, target: str = "x86_64-linux-direct-elf"
    ) -> tuple[Path, Path]:
        artifact = directory / "checked.tsv"
        receipt = directory / "execution.tsv"
        artifact.write_text(artifact_text(), encoding="utf-8")
        digest = sha256(artifact.read_bytes()).hexdigest()
        receipt.write_text(receipt_text(digest, target=target), encoding="utf-8")
        return artifact, receipt

    def test_exact_x86_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            artifact, receipt = self.write_pair(Path(temporary))
            validate_files(artifact, receipt)

    def test_exact_fragment_host_semantics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            artifact, receipt = self.write_pair(
                Path(temporary), target="fragment-mock:mali-g57-valhall"
            )
            validate_files(artifact, receipt)

    def test_vector_cannot_replace_covector(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            artifact, receipt = self.write_pair(root)
            artifact.write_text(
                artifact.read_text(encoding="utf-8").replace(
                    "value\tphi\tcovector", "value\tphi\tvector"
                ),
                encoding="utf-8",
            )
            new_digest = sha256(artifact.read_bytes()).hexdigest()
            receipt.write_text(
                receipt.read_text(encoding="utf-8").replace(
                    "artifact_sha256\t" + sha256(artifact_text().encode()).hexdigest(),
                    "artifact_sha256\t" + new_digest,
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ReceiptError, "phi must be covector"):
                validate_files(artifact, receipt)

    def test_far_coordinate_cannot_disappear(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            artifact, receipt = self.write_pair(root)
            old = artifact.read_text(encoding="utf-8")
            artifact.write_text(old.replace(X, coordinates(3, 4, 12, 0)), encoding="utf-8")
            digest = sha256(artifact.read_bytes()).hexdigest()
            receipt.write_text(receipt_text(digest), encoding="utf-8")
            with self.assertRaisesRegex(ReceiptError, "hostile R128 fixture"):
                validate_files(artifact, receipt)

    def test_wrong_result_fails_at_rhs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            artifact, receipt = self.write_pair(Path(temporary))
            receipt.write_text(
                receipt.read_text(encoding="utf-8").replace(
                    "contraction\texact_integer\t190",
                    "contraction\texact_integer\t189",
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ReceiptError, "expected 190, observed 189"):
                validate_files(artifact, receipt)

    def test_fragment_hardware_cannot_be_claimed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            artifact, receipt = self.write_pair(
                Path(temporary), target="fragment-mock:mali-g57-valhall"
            )
            receipt.write_text(
                receipt.read_text(encoding="utf-8").replace(
                    "hardware_execution\tSKIP", "hardware_execution\tPASS"
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ReceiptError, "must remain SKIP"):
                validate_files(artifact, receipt)

    def test_forbidden_fallback_is_not_tolerated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            artifact, receipt = self.write_pair(Path(temporary))
            receipt.write_text(
                receipt.read_text(encoding="utf-8").replace(
                    "fallback\tRefC\tABSENT", "fallback\tRefC\tPRESENT"
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ReceiptError, "forbidden fallback RefC"):
                validate_files(artifact, receipt)

    def test_missing_hostile_case_is_a_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            artifact, receipt = self.write_pair(root)
            hostile = root / "hostile"
            hostile.mkdir()
            write_hostile_receipts(hostile)
            (hostile / "hostile-theorem_ambiguous.tsv").unlink()
            with self.assertRaisesRegex(ReceiptError, "missing hostile receipt"):
                validate_complete_files(artifact, receipt, hostile)

    def test_hostile_receipts_bind_the_rejected_source_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            artifact, receipt = self.write_pair(root)
            hostile = root / "hostile"
            hostile.mkdir()
            write_hostile_receipts(hostile)
            source = hostile / "hostile-theorem_absent.idric"
            source.write_text("different hostile source\n", encoding="utf-8")
            with self.assertRaisesRegex(ReceiptError, "not bound to its source bytes"):
                validate_complete_files(artifact, receipt, hostile)

    def test_downstream_pass_after_hostile_failure_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            artifact, receipt = self.write_pair(root)
            hostile = root / "hostile"
            hostile.mkdir()
            write_hostile_receipts(hostile)
            failure = hostile / "hostile-theorem_absent.tsv"
            failure.write_text(
                failure.read_text(encoding="utf-8").replace(
                    "core_typecheck\tSKIP\tblocked_by=constraint_resolution",
                    "core_typecheck\tPASS\tunchecked continuation",
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ReceiptError, "fabricated a downstream result"):
                validate_complete_files(artifact, receipt, hostile)


if __name__ == "__main__":
    unittest.main()
