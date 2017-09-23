#!/usr/bin env python3

import os
import sys
import re

LABDIR=sys.argv[1]

def format_label(label_feat):
    lf = label_feat
    phone_durs = "{} {}".format(lf['p_start'], lf['p_end'])
    p1_p7 = "{}^{}-{}+{}={}@{}_{}".format(lf['p1'], lf['p2'], lf['p3'], lf['p4'], lf['p5'], lf['p6'], lf['p7'])
    A = "/A:{}_{}_{}".format(lf['a1'], lf['a2'], lf['a3'])
    B = "/B:{}-{}-{}@{}-{}&{}-{}#{}-{}${}-{}!{}-{};{}-{}|{}".format(
            lf['b1'], lf['b2'], lf['b3'], lf['b4'], lf['b5'], lf['b6'], lf['b7'], lf['b8'],
            lf['b9'], lf['b10'], lf['b11'], lf['b12'], lf['b13'], lf['b14'], lf['b15'], lf['b16'])
    C = "/C:{}+{}+{}".format(lf['c1'], lf['c2'], lf['c3'])
    D = "/D:{}_{}".format(lf['d1'], lf['d2'])
    E = "/E:{}+{}@{}+{}&{}+{}#{}+{}".format(lf['e1'], lf['e2'], lf['e3'], lf['e4'],
        lf['e5'], lf['e6'], lf['e7'], lf['e8'])
    F = "/F:{}_{}".format(lf['f1'], lf['f2'])
    G = "/G:{}_{}".format(lf['g1'], lf['g2'])
    H = "/H:{}={}^{}={}|{}".format(lf['h1'], lf['h2'], lf['h3'], lf['h4'], lf['h5'])
    I = "/I:{}={}".format(lf['i1'], lf['i2'])
    J = "/J:{}+{}-{}".format(lf['j1'], lf['j2'], lf['j3'])
    return phone_durs + " " + p1_p7 + A + B + C + D + E + F + G + H + I + J


def fullcontext_regex():
    #p1^p2-p3+p4=p5@p6-p7/A:a1_a2_a3/B:b1-b2-b3@b4-b5&b6-b7#b8-b9$b10-b11!b12-b13;b14-b15|b16/C:c1+c2+c3/D:d1_d2/E:e1+e2@e3+e4&e5+e6#e7+e8/F:f1_f2/G:g1_g2/H:h1=h2ˆh3=h4|h5/I:i1=i2/J:j1+j2-j3
    #"%s^%s-%s+%s=%s@xx_xx/A:%s_%s_%s/B:xx-xx-xx@xx-xx&xx-xx#xx-xx$xx-xx!xx-xx;xx-xx|xx/C:%s+%s+%s/D:%s_%s/E:xx+xx@xx+xx&xx+xx#xx+xx/F:%s_%s/G:%s_%s/H:xx=xx^xx=xx|xx/I:%s=%s/J:%d+%d-%d"
    #%s^%s-%s+%s=%s@%d_%d/A:%s_%s_%s/B:%d-%d-%d@%d-%d&%d-%d#%d-%d$%d-%d!%s-%s;%s-%s|%s/C:%s+%s+%s/D:%s_%s/E:%s+%d@%d+%d&%d+%d#%s+%s/F:%s_%s/G:%s_%s/H:%d=%d^%d=%d|%s/I:%s=%s/J:%d+%d-%d"

    def g(name, gtype):
        if gtype == "phoneme":
            phoneme = "(?P<{}>[a-zA-Z#@0-9]+?)".format(name)
            return phoneme
        elif gtype == "integer":
            integer = "(?P<{}>[0-9]+)".format(name)
            return integer
        elif gtype == "integer_discard_neg":
            integer = "-?(?P<{}>[0-9]*)".format(name)
            return integer
        elif gtype == "integer_or_nothing":
            integer = "(?P<{}>[0-9]*)".format(name)
            return integer
        elif gtype == "integer_or_x":
            integer_or_x = "(?P<{}>[x0-9]+)".format(name)
            return integer_or_x
        elif gtype == "logical":
            logical = "(?P<{}>[01])".format(name)
            return logical
        elif gtype == "logical_or_x": # xx 
            logical_or_x = "(?P<{}>x?[x01])".format(name)
            return logical_or_x
        elif gtype == "pos" or gtype == "pos_or_0":
            pos = "(?P<{}>[a-zA-Z#@_0-9]+?)".format(name)
            return pos
        elif gtype == "TOBI":
            return "(?P<{}>[NONE0-9]+)".format(name)
        elif gtype == "TOBI_or_x":
            return "(?P<{}>[xNONE0-9]+)".format(name)
        elif gtype == "":
            return "(?P<{}>.*)".format(name)
        else:
            raise ValueError("Unknown type")
    phone_durs = "^" + g("p_start", "integer") + r"\s+" + g("p_end", "integer") + r"\s+"
    # p1^p2-p3+p4=p5@p6_p7 "%s^%s-%s+%s=%s@xx_xx" or "%s^%s-%s+%s=%s@%d_%d"
    p1_p7 = (g("p1", "phoneme") +
             r"\^" + g("p2", "phoneme") +
             r"\-" + g("p3", "phoneme") +
             r"\+" + g("p4", "phoneme") +
             "=" + g("p5", "phoneme") +
             "@" + g("p6", "integer_or_x") +
             "_" + g("p7", "integer_or_x"))
    # /A:a1_a2_a3 (new: %s_%s_%s)
    A = ("/A:" + g("a1", "logical") +
         "_" + g("a2", "logical") +
         "_" + g("a3", "integer"))
    # /B:b1-b2-b3@b4-b5&b6-b7#b8-b9$b10-b11!b12-b13;b14-b15|b16
    B = ("/B:" + g("b1", "logical_or_x") + # b1
         r"\-" + g("b2", "logical_or_x") + # b2
         r"\-" + g("b3", "integer_or_x") + # b3
         "@" + g("b4", "integer_or_x") + #b4
         r"\-" + g("b5", "integer_or_x") + #b5
         "&" + g("b6", "integer_or_x") + #b6
         r"\-" + g("b7", "integer_or_x") + # b7
         r"\#" + g("b8", "integer_or_x") + # b8
         r"\-" + g("b9", "integer_or_x") + # b9
         r"\$" + g("b10", "integer_or_x") + # b10
         r"\-" + g("b11", "integer_or_x") + # b11         
         r"\!" + g("b12", "integer_or_x") + # b12
         r"\-" + g("b13", "integer_or_x") + # b13
         ";" + g("b14", "integer_or_x") + # b14
         r"\-" + g("b15", "integer_or_x") + # b15
         r"\|" + g("b16", "phoneme") # b16
        )
    # /C:c1+c2+c3
    C = ("/C:" + g("c1", "integer_discard_neg") + # c1 (logical, but the last label on some files of the siwis dataset contains garbage for this value)
         r"\+" + g("c2", "integer_discard_neg") + # c2 (logical, but the last label on some files of the siwis dataset contains garbage for this value)
         r"\+" + g("c3", "integer_discard_neg") # c3 (integer, but the last label on some files of the siwis dataset contains garbage for this value)
        )
    #/D:d1_d2
    D = "/D:" + g("d1", "pos_or_0") + "_" + g("d2", "integer")
    #/E:e1+e2@e3+e4&e5+e6#e7+e8
    E = ("/E:" + g("e1", "pos_or_0") +
         r"\+" + g("e2", "integer_or_x") +
         r"@" + g("e3", "integer_or_x") +
         r"\+" + g("e4", "integer_or_x") +
         r"&" + g("e5", "integer_or_x") +
         r"\+" + g("e6", "integer_or_x") +
         r"#" + g("e7", "integer_or_x") +
         r"\+" + g("e8", "integer_or_x")
        )
    #/F:f1_f2
    F = "/F:" + g("f1", "pos") + "_" + g("f2", "integer")
    #/G:g1_g2
    G = "/G:" + g("g1", "integer") + "_" + g("g2", "integer")
    #/H:h1=h2ˆh3=h4|h5
    H = ("/H:" + g("h1", "integer_or_x") + 
         "=" + g("h2", "integer_or_x") +
         "[@|^]" + g("h3", "integer_or_x") + # HTS docs says "use ^", but french siwis dataset uses @
         "=" + g("h4", "integer_or_x") + 
         "\|" + g("h5", "TOBI_or_x")
        )
    #/I:i1=i2
    I = "/I:" + g("i1", "integer_discard_neg") + "=" + g("i2", "integer") # i1: integer, last label garbage
    #/J:j1+j2-j3
    J = "/J:" + g("j1", "integer_or_nothing") + r"\+" + g("j2", "integer_or_nothing") + r"\-" + g("j3", "integer_or_nothing")
    full_pattern = phone_durs + p1_p7 + A + B + C + D + E + F + G + H + I + J
    comp_pat = re.compile(full_pattern)
    return comp_pat

def parse_label(label, comp_pat=fullcontext_regex()):
    match = re.match(comp_pat, label)
    if match is None:
        raise ValueError("No match in label:\n{}".format(label))
    return match.groupdict()

def read_labelfile(labelfn, comp_pat=fullcontext_regex()):
    output = []
    with open(labelfn, "r") as fh:
        output = [parse_label(line, comp_pat=comp_pat) for line in fh.readlines()]
    return output


def progress_bar(item, num_items):
    prev_percent = 100*(item-1)//num_items
    percent = 100*item//num_items
    update = prev_percent//5 != percent//5
    if update:
        sys.stdout.write('\r')
        sys.stdout.write("[%-40s] %d%%" % ('='*((2*percent)//5), percent))
        sys.stdout.flush()
    if item == num_items-1:
        sys.stdout.write('\r')
        sys.stdout.write("[%-40s] %d%%" % ('='*(40), 100))
        sys.stdout.write('\n')
        sys.stdout.flush()



def extract_mono_info(labfile):
    phonegrp = "([a-zA-Z@#0-9]+)"
    pattern = re.compile(r"([0-9]+) ([0-9]+) " + phonegrp + r"\^" + phonegrp + r"\-" + phonegrp + ".*")
    with open(labfile, "r") as f:
        lines = f.readlines()
    output = []
    for linenum, line in enumerate(lines):
        a = re.match(pattern, line)
        if a is None:
            print("ERROR on file {} at line {}:\n{}\nPattern not found".format(labfile, linenum+1, line), file=sys.stderr)
            sys.exit(1)
        t_start = a.group(1)
        t_end = a.group(2)
        phone = a.group(5)
        output.append((t_start, t_end, phone))
    return output

def full_to_mono(fulldir, monodir):
    labfiles = list(os.listdir(fulldir))
    for labfilei, labfile in enumerate(labfiles):
        progress_bar(labfilei, len(labfiles))
        labinfo = extract_mono_info(os.path.join(fulldir, labfile))
        with open(os.path.join(monodir, labfile), "w") as fd:
            print("\n".join([" ".join(x) for x in labinfo]), file=fd)

def replace_phone_N_by_n(labinfo):
    phone_features = ["p1", "p2", "p3", "p4", "p5", "b16"]
    output = []
    for label in labinfo:
        for ph in phone_features:
            if label[ph] == "N":
                label[ph] = "n"
        output.append(label)
    return output


def replace_phone_at_by_ax(labinfo):
    phone_features = ["p1", "p2", "p3", "p4", "p5", "b16"]
    output = []
    for label in labinfo:
        for ph in phone_features:
            if label[ph] == "@":
                label[ph] = "ax"
        output.append(label)
    return output


def fix_lastlabel(labinfo):
    output = labinfo
    for (feat, expected) in [("c1", "0"), ("c2", "0"), ("c3", "0"), ("f1", "0"),
                             ("f2", "0"), ("i1", "0"), ("i2", "0"), ("p4", "xx"),
                             ("p5", "xx")]:
        if output[-1][feat] != expected:
            output[-1][feat] = expected
    for feat in ["j1", "j2", "j3"]:
        if output[-1][feat] == "":
            output[-1][feat] = output[-2][feat]
    return output

def replace_x_by_xx(labinfo):
    output = []
    affected_feats = (["p" + str(x) for x in range(1,8)] + ["b" + str(x) for x in range(1,17)] +
                      ["e" + str(x) for x in range(1, 9)] + ["h" + str(x) for x in range(1,6)])
    for label in labinfo:
        for feat in affected_feats:
            if label[feat] == "x":
                label[feat] = "xx"
        output.append(label)
    return output

def ensure_c1_c2_logical(labinfo):
    output = []
    for label in labinfo:
        if label["c1"] != "1":
            label["c1"] = "0"
        if label["c2"] != "1":
            label["c2"] = "0"
        output.append(label)
    return output

def fix_labinfo(labinfo):
    labinfo = replace_phone_N_by_n(labinfo)
    labinfo = replace_phone_at_by_ax(labinfo)
    labinfo = replace_x_by_xx(labinfo)
    labinfo = fix_lastlabel(labinfo)
    labinfo = ensure_c1_c2_logical(labinfo)
    return labinfo

def orig_to_full(origdir, fulldir):
    labfiles = list(os.listdir(origdir))
    comp_pat = fullcontext_regex()
    for labfilei, labfile in enumerate(labfiles):
        progress_bar(labfilei, len(labfiles))
        labinfo = read_labelfile(os.path.join(origdir, labfile), comp_pat = comp_pat)
        labinfo = fix_labinfo(labinfo)
        with open(os.path.join(fulldir, labfile), "w") as fd:
            print("\n".join([format_label(x) for x in labinfo]), file=fd)


ORIG=os.path.join(LABDIR, "full_orig")
FULL=os.path.join(LABDIR, "full")
MONO = os.path.join(LABDIR, "mono")

print("1/2 Fix labels")
orig_to_full(ORIG, FULL)
print("2/2 Full to monophone labels")
full_to_mono(FULL, MONO)

