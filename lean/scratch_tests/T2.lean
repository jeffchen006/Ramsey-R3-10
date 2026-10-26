import R310.LP.Cases
import R310.LP.Data.GrMtfTable
open R310.LP R310.LP.Data
theorem t_enum : enumOK 161 true surv_gr_mtf lpkill_gr_mtf = true := by decide +kernel
