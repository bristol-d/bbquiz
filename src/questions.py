import mcq
import shortanswer
import maq
import numeric
import jumbled
import blank

QUESTION_TYPES = {
    'mcq': mcq.Mcq,
    'shortanswer': shortanswer.ShortAnswer,
    'maq': maq.Maq,
    'numeric': numeric.Numeric,
    'jumbled': jumbled.Jumbled,
    'blanks': blank.FillInTheBlank
}
