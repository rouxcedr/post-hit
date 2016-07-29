import collections

State = collections.namedtuple(
            "State",
            ("state_number", "mnemonic", "description", "color_name",
             "color_code")
        )

states = {
  "1_TssA": State(1, "TssA", "Active TSS", "Red", "#FF0000"),
  "2_PromU": State(2, "PromU", "Promoter Upstream TSS", "Orange Red",
                   "#FF4500"),
  "3_PromD1": State(3, "PromD1", "Promoter Downstream TSS 1",
                    "Orange Red", "#FF4500"),
  "4_PromD2": State(4, "PromD2", "Promoter Downstream TSS 2",
                    "Orange Red", "#FF4500"),
  "5_Tx5'": State(5, "Tx5", "Transcribed - 5' preferential", "Green",
                 "#008000"),
  "6_Tx": State(6, "Tx", "Strong transcription", "Green", "#008000"),
  "7_Tx3'": State(7, "Tx3", "Transcribed - 3' preferential", "Green",
                 "#008000"),
  "8_TxWk": State(8, "TxWk", "Weak transcription", "Lighter Green",
                  "#009600"),
  "9_TxReg": State(9, "TxReg", "Transcribed & regulatory (Prom/Enh)",
                   "Electric Lime", "#C2E150"),
  "10_TxEnh5'": State(10, "TxEnh5",
                     "Transcribed 5' preferential and Enh",
                     "Electric Lime", "#C2E150"),
  "11_TxEnh3'": State(11, "TxEnh3",
                     "Transcribed 3' preferential and Enh",
                     "Electric Lime", "#C2E150"),
  "12_TxEnhW": State(12, "TxEnhW",
                     "Transcribed and Weak Enhancer Electric",
                     "Lime", "#C2E150"),
  "13_EnhA1": State(13, "EnhA1", "Active Enhancer 1", "Orange",
                    "#FFC34D"),
  "14_EnhA2": State(14, "EnhA2", "Active Enhancer 2", "Orange",
                    "#FFC34D"),
  "15_EnhAF": State(15, "EnhAF", "Active Enhancer Flank", "Orange",
                    "#FFC34D"),
  "16_EnhW1": State(16, "EnhW1", "Weak Enhancer 1", "Yellow",
                    "#FFFF00"),
  "17_EnhW2": State(17, "EnhW2", "Weak Enhancer 2", "Yellow",
                    "#FFFF00"),
  "18_EnhAc": State(18, "EnhAc", "Primary H3K27ac possible Enhancer",
                    "Yellow", "#FFFF00"),
  "19_DNase": State(19, "DNase", "Primary DNase", "Lemon",
                    "#FFFF66"),
  "20_ZNF/Rpts": State(20, "ZNF/Rpts", "ZNF genes & repeats",
                       "Aquamarine", "#66CDAA"),
  "21_Het": State(21, "Het", "Heterochromatin", "Light Purple",
                  "#8A91D0"),
  "22_PromP": State(22, "PromP", "Poised Promoter", "Pink",
                    "#E6B8B7"),
  "23_PromBiv": State(23, "PromBiv", "Bivalent Promoter",
                      "Dark Purple", "#7030A0"),
  "24_ReprPC": State(24, "ReprPC", "Repressed Polycomb", "Gray",
                     "#808080"),
  "25_Quies": State(25, "Quies", "Quiescent/Low", "White",
                    "#FFFFFF"),
}

json = []
for key in states:
  json.append({
    "id": key,
    "state_number": states[key].state_number,
    "mnemonic": states[key].mnemonic,
    "description": states[key].description,
    "color": states[key].color_code
  })

print(json)