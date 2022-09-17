import bbquiz.mcq           as mcq
import bbquiz.shortanswer   as shortanswer
import bbquiz.longanswer    as longanswer
import bbquiz.maq           as maq
import bbquiz.maq2          as maq2
import bbquiz.numeric       as numeric
import bbquiz.jumbled       as jumbled
import bbquiz.blank         as blank

QUESTION_TYPES = {
    'mcq': mcq.Mcq,
    'shortanswer': shortanswer.ShortAnswer,
    'longanswer': longanswer.LongAnswer,
    'maq': maq.Maq,
    'numeric': numeric.Numeric,
    'jumbled': jumbled.Jumbled,
    'blanks': blank.FillInTheBlank,
    'multi': maq2.MultipleAnswerDropdown
}
