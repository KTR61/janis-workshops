from janis_core import WorkflowBuilder, Array, String

# Import bioinformatics types
from janis_bioinformatics.data_types import (
    FastqGzPairedEnd,
    FastaWithIndexes,
    VcfTabix,
)

# Import bioinformatics tools
from janis_bioinformatics.tools.bwa import BwaMemLatest
from janis_bioinformatics.tools.samtools import SamToolsView_1_9
from janis_bioinformatics.tools.gatk4 import (
    Gatk4MarkDuplicates_4_1_4,
    Gatk4SortSam_4_1_4,
    Gatk4SetNmMdAndUqTags_4_1_4,
)

# Add tools import here
from tools_solution import (
    Gatk4BaseRecalibrator_4_1_4,
    Gatk4ApplyBQSR_4_1_4,
    Gatk4HaplotypeCaller_4_1_4,
)

# Construct the workflow here
w = WorkflowBuilder("variantcaller")

# inputs
w.input("sample_name", String)
w.input("read_group", String)
w.input("fastq", FastqGzPairedEnd)
w.input("reference", FastaWithIndexes)
# add known_sites input here
w.input("known_sites", Array(VcfTabix))

# Use `bwa mem` to align our fastq paired ends to the reference genome
w.step(
    "bwamem",  # step identifier
    BwaMemLatest(
        reads=w.fastq,
        readGroupHeaderLine=w.read_group,
        reference=w.reference,
        markShorterSplits=True,  # required for MarkDuplicates
    ),
)

# Use `samtools view` to convert the aligned SAM to a BAM
#   - Use the output `out` of the bwamem step
w.step(
    "samtoolsview", SamToolsView_1_9(sam=w.bwamem.out),
)

# Use `gatk4 MarkDuplicates` on the output of samtoolsview
#   - The output of BWA is query-grouped, providing "queryname" is good enough
w.step(
    "markduplicates",
    Gatk4MarkDuplicates_4_1_4(bam=w.samtoolsview.out, assumeSortOrder="queryname"),
)
# Use `gatk4 SortSam` on the output of markduplicates
#   - Use the "coordinate" sortOrder
w.step("sortsam", Gatk4SortSam_4_1_4(bam=w.markduplicates.out, sortOrder="coordinate",))

# Use `gatk4 SetNmMdAndUqTags` to calculate standard tags for BAM
w.step(
    "fix_tags", Gatk4SetNmMdAndUqTags_4_1_4(bam=w.sortsam.out, reference=w.reference,),
)

# Add the Base Quality Score Recalibration steps here!

# Generate the recalibration table from the bam in fix_tags
w.step(
    "baserecalibration",
    Gatk4BaseRecalibrator_4_1_4(
        bam=w.fix_tags.out, reference=w.reference, knownSites=w.known_sites
    ),
)

# Use the recalibration table to fix the bam from fix_tags
w.step(
    "applybqsr",
    Gatk4ApplyBQSR_4_1_4(
        bam=w.fix_tags.out,
        reference=w.reference,
        recalFile=w.baserecalibration.out_recalibration_report,
    ),
)

# Use HaplotypeCaller as our variant caller
w.step(
    "haplotypecaller",
    Gatk4HaplotypeCaller_4_1_4(bam=w.applybqsr.out_bam, reference=w.reference),
)

w.output("out_recalibration_table", source=w.baserecalibration.out_recalibration_report)
w.output("out_bam", source=w.applybqsr.out_bam)
w.output("out_assembledbam", source=w.haplotypecaller.out_bam)
w.output("out_variants", source=w.haplotypecaller.out_vcf)


if __name__ == "__main__":

    import json
    from janis_core.translations.cwl import CwlTranslator

    out = CwlTranslator.translate_workflow_to_all_in_one(w).save()
    with open("/Users/franklinmichael/Desktop/tmp/janis/bcc/vc.json", "w+") as f:
        json.dump(out, f)

    # w.translate("cwl", export_path="~/Desktop/tmp/janis/bcc/", to_disk=True)
