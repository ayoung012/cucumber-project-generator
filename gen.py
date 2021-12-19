from random import shuffle, choice, sample
import os
import re
import sys

step_def_location="src/test/java"
step_def_package=["generated", "step", "definitions"]
feature_location="src/test/features"

pronouns=["Given", "Then", "When"]
num_features = 1000
scenarios_per_feature = 10
num_step_definitions = 756 # * 3 (Given, When, Then)
# If the below is divisible by num_step_definitions, there will be no undefined steps
step_def_per_file = 7 # * 3 (Given, When, Then)

def wildcard():
    return "{string}"

def startGlue(pronoun, word):
    return ("@" + pronoun + "(\"") + word + " "

def endGlue():
    return "\")"

def methodDef(name, numParams):
    return "public final void " + name + "(" + ', '.join(["String param" + str(i) for i in range(numParams)]) + ") { }"

def startSentence(pronoun, word):
    return "    " + (pronoun if len(pronoun) != 0 else "") + " " + word + " "

def endSentence():
    return "" 

def glue(methodName, pronoun, words, wildIndexes):
    words=(words.copy())
    for n in wildIndexes:
        words.insert(n, wildcard())
    return "    " + startGlue(pronoun, words[0]) + " ".join(words[1:]) + endGlue() + "\n    " + methodDef(methodName, len(wildIndexes))

def glueFile(class_name, glues):
    file = "package " + ".".join(step_def_package) + ";\n\n"
    for pronoun in pronouns:
        file += "import io.cucumber.java.en." + pronoun + ";\n"
    file += "\npublic final class " + class_name + " {"
    for pronoun in pronouns:
        file += "\n\n" + "\n\n".join([glue(pronoun+str(i), *glues[pronoun][i]) for i in range(len(glues[pronoun]))])
    return file + "\n}"



sentence_last_pronoun = ""
def sentence(pronoun, words, wildIndexes, params):
    global sentence_last_pronoun
    words=(words.copy())
    for n in wildIndexes:
        words.insert(n,"\"" + choice(params) + "\"")
    if pronoun is sentence_last_pronoun:
        return startSentence("And", words[0]) + " ".join(words[1:]) + endSentence()
    else:
        sentence_last_pronoun=pronoun
        return startSentence(pronoun, words[0]) + " ".join(words[1:]) + endSentence()

def paragraph(sentencer, words):
    return "\n".join([sentencer(words) for i in range(4)])

def scenario(name, sentencer, glues, params):
    return "  Scenario: " + name + "\n" + \
            "\n".join([sentencer(*(choice(glues["Given"])), params) for i in range(4)]) + "\n" + \
            "\n".join([sentencer(*(choice(glues["When"])), params) for i in range(1)]) + "\n" + \
            "\n".join([sentencer(*(choice(glues["Then"])), params) for i in range(2)]) + "\n"

def feature(name_arr, sentencer, glues, params):
    name = " ".join(name_arr)
    return "Feature: " + name + "\n\n" + \
        "\n".join([scenario(name + " " + str(i), sentencer, glues, params) for i in range(scenarios_per_feature)])


def generateGlues(pronoun, dictionary, n):
    w=7
    shutter_speed = 200
    glues = []
    i = 0
    for j in range(shutter_speed - 1, n * shutter_speed - 1, shutter_speed):
        shutter_start = i % len(dictionary)
        shutter_end = j % len(dictionary)
        if shutter_start > shutter_end:
            vocab = dictionary[shutter_start:] + dictionary[:shutter_end]
        else:
            vocab = dictionary[shutter_start:shutter_end]
        glue = generateGlue(pronoun, vocab, w)
        glues.append(glue)
        i = j
    return glues

def generateGlue(pronoun, vocab, n):
    shuffle(vocab)
    return [pronoun, vocab[:n], [3, 6]]

def main():
    if len(sys.argv) < 2:
        print("Usage: " + sys.argv[0] + " <dictionary.txt>")
        return
    if not os.path.exists(sys.argv[1]):
        print("Error: dictionary provided is not a valid file")
        return
    with open(sys.argv[1], "r") as df:
        dictionary = df.read().splitlines()
    shuffle(dictionary)
    params = dictionary[:1000]
    r = re.compile("^[a-zA-Z]+$")
    simple=list(filter(r.match, dictionary))
    class_names = simple[:int(num_step_definitions / step_def_per_file)]
    feature_names = [sample(simple, 3) for i in range(num_features)]
    glues = dict()
    for pronoun in pronouns:
        glues[pronoun] = generateGlues(pronoun, dictionary, num_step_definitions)
    if not os.path.exists(step_def_location + "/" + "/".join(step_def_package)):
        os.makedirs(step_def_location + "/" + "/".join(step_def_package))
    if not os.path.exists(feature_location):
        os.makedirs(feature_location)
    i = 0
    c = 0
    for j in range(step_def_per_file - 1, num_step_definitions, step_def_per_file):
        glues_in_file = dict()
        for pronoun in pronouns:
            glues_in_file[pronoun] = glues[pronoun][i:j]
        class_name = class_names[c].capitalize() + "Steps"
        with open(step_def_location + "/" + class_name + ".java", "w") as f:
            print(glueFile(class_name, glues_in_file), file=f)
        i = j
        c+=1
    for name_arr in feature_names:
        filename = '_'.join(name_arr) + '.feature'
        with open(feature_location + "/" + filename, "w") as e:
            print(feature(name_arr, sentence, glues, params), file=e)


main()
