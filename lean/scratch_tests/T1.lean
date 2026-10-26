import R310.LP.Cases
import R310.LP.Data.GrMtfTable
open R310.LP R310.LP.Data
theorem t_lpk : lpkOK certs_gr_mtf lpkill_gr_mtf true = true := by decide +kernel
theorem t_t9 : t9OK certs_gr_mtf t9_gr_mtf_U8 U_U8 true = true := by decide +kernel
