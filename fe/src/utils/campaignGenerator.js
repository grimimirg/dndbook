// pick() handles string arrays with optional [string, weight] pairs.
// For paired data (narr + label) we use objects {n, l} to avoid ambiguity.
function pick(arr) {
  const total = arr.reduce((s, x) => s + (Array.isArray(x) ? x[1] : 1), 0);
  let r = Math.random() * total;
  for (const x of arr) {
    r -= Array.isArray(x) ? x[1] : 1;
    if (r <= 0) return Array.isArray(x) ? x[0] : x;
  }
  const last = arr.at(-1);
  return Array.isArray(last) ? last[0] : last;
}

// ═══════════════════════════════════════════════════════════════════════════════
// ITALIANO
// ═══════════════════════════════════════════════════════════════════════════════

const it = {
  luoghi: [
    'Nelle antiche foreste di', 'Nelle montagne spezzate di', 'Nelle pianure desolate di',
    'Nelle paludi silenziose di', 'Nelle rovine sommerse di', 'Nei deserti ardenti di',
    'Nelle isole nebbiose di', 'Nelle catacombe dimenticate di', 'Nei porti oscuri di',
    'Nelle valli proibite di', 'Nei boschi maledetti di', 'Nelle scogliere battute dai venti di',
  ],
  nomi: [
    'Valdrath', 'Morthein', 'Caer Solenne', 'Duskmore', 'Aelundra',
    'Ferraspina', 'Cremora', 'Noctivale', 'Ironshard', 'Valthara',
    'Cinderhollow', 'Ombraluna', 'Greymantle', 'Fossatenebre', 'Aurenfall',
  ],
  ambientazioni: [
    'foreste / natura selvaggia', 'montagne / rovine', 'città / intrighi di corte',
    'paludi / terre oscure', 'deserti / civiltà perdute', 'isole / mare aperto',
    'dungeon / catacombe', 'piani elementali', 'terre di frontiera',
  ],
  antagonisti: [
    {n: "un lich di potere inimmaginabile", l: "lich antico"},
    {n: "un culto dedito al risveglio di un dio dimenticato", l: "culto oscuro"},
    {n: "un drago corrotto dall'odio millenario", l: "drago corrotto"},
    {n: "un nobile traditore che ha stretto un patto con i demoni", l: "nobile traditore"},
    {n: "una strega che tesse le sue trame da secoli nell'ombra", l: "strega millenaria"},
    {n: "un condottiero spietato alla guida di un'orda inarrestabile", l: "signore della guerra"},
    {n: "uno spirito antico che la terra stessa ha rigettato", l: "spirito antico"},
    {n: "un'entità venuta da oltre il velo della realtà", l: "entità extradimensionale"},
    {n: "una gilda di assassini che muove i fili del potere dall'ombra", l: "gilda oscura"},
    {n: "un arcimago folle convinto di voler salvare il mondo distruggendolo", l: "arcimago rinnegato"},
    [{n: "un vampiro signore che ha assoggettato un'intera regione", l: "vampiro signore"}, 0.7],
    [{n: "una dea caduta che vuole riconquistare la sua divinità a qualsiasi costo", l: "dea caduta"}, 0.5],
  ],
  minacce: [
    "sta diffondendo una corruzione silenziosa che divora la terra",
    "ha spezzato l'equilibrio tra i vivi e i morti",
    "raduna forze abbastanza potenti da rovesciare ogni regno conosciuto",
    "cerca un artefatto la cui riscoperta porterebbe la fine di un'era",
    "ha già fatto cadere tre città nel silenzio, e il silenzio avanza",
    "manipola i potenti dal buio, e nessuno sa ancora di chi fidarsi",
    "sta aprendo portali verso piani di esistenza che non dovrebbero toccare questo mondo",
    "ha posto una maledizione sull'intera regione: i raccolti marciscono, i pozzi si prosciugano",
    "recluta disperati e reietti, promettendo potere in cambio di devozione cieca",
    "ha rubato qualcosa di sacro, e la sua assenza si sente come una ferita aperta nel mondo",
  ],
  hooks: [
    "Siete stati ingaggiati — o forse non avete avuto altra scelta",
    "Il destino, la sfortuna, o forse entrambi vi hanno portato fin qui",
    "Qualcuno di cui vi fidavate vi ha chiesto questo come ultimo favore",
    "Avete visto qualcosa che non avreste dovuto vedere, e ora non potete più ignorarlo",
    "La vostra strada e quella della minaccia si sono incrociate una volta di troppo",
    "C'è un debito da saldare — di sangue, di onore, o di oro",
    "Una visione, un sogno ricorrente, una profezia: il posto vi perseguita da settimane",
    "Eravate nel posto sbagliato al momento sbagliato — o forse quello giusto",
    "Qualcuno che amate è già là dentro",
    "Vi è stato detto che siete gli unici a poterlo fare — forse è vero, forse no",
  ],
  obiettivi: [
    {n: "sconfiggere l'antagonista prima che completi il suo piano", l: "sconfitta dell'antagonista"},
    {n: "trovare e distruggere l'artefatto che lo alimenta", l: "distruzione dell'artefatto"},
    {n: "spezzare la maledizione prima che divori tutto", l: "rottura della maledizione"},
    {n: "scoprire la verità dietro le sparizioni e mettere fine al terrore", l: "indagine e risoluzione"},
    {n: "liberare la regione dall'occupazione e restituirla ai suoi abitanti", l: "liberazione del territorio"},
    {n: "recuperare qualcosa di prezioso prima che cada nelle mani sbagliate", l: "recupero dell'oggetto"},
    {n: "chiudere i portali e sigillare ciò che non doveva passare", l: "sigillo dimensionale"},
    {n: "sopravvivere, con quanta più verità in tasca possibile", l: "sopravvivenza e scoperta"},
    {n: "trovare un'alleanza tra fazioni nemiche prima che sia troppo tardi", l: "diplomazia impossibile"},
    {n: "riportare alla luce una storia sepolta che qualcuno ha tutto l'interesse a tenere nascosta", l: "rivelazione della verità"},
  ],
  labels: { setting: 'Ambientazione', antagonist: 'Antagonista', objective: 'Obiettivo' },
};

// ═══════════════════════════════════════════════════════════════════════════════
// ENGLISH (fallback for all other locales)
// ═══════════════════════════════════════════════════════════════════════════════

const en = {
  luoghi: [
    'In the ancient forests of', 'In the shattered mountains of', 'In the desolate plains of',
    'In the silent swamps of', 'In the sunken ruins of', 'In the scorching deserts of',
    'In the mist-shrouded islands of', 'In the forgotten catacombs of', 'In the shadowed ports of',
    'In the forbidden valleys of', 'In the cursed woodlands of', 'In the wind-battered cliffs of',
  ],
  nomi: [
    'Valdrath', 'Morthein', 'Caer Solenne', 'Duskmore', 'Aelundra',
    'Ferraspina', 'Cremora', 'Noctivale', 'Ironshard', 'Valthara',
    'Cinderhollow', 'Ombraluna', 'Greymantle', 'Fossatenebre', 'Aurenfall',
  ],
  ambientazioni: [
    'forests / wilderness', 'mountains / ruins', 'city / court intrigue',
    'swamps / dark lands', 'deserts / lost civilizations', 'islands / open sea',
    'dungeon / catacombs', 'elemental planes', 'frontier lands',
  ],
  antagonisti: [
    {n: "a lich of unimaginable power", l: "ancient lich"},
    {n: "a cult devoted to awakening a forgotten god", l: "dark cult"},
    {n: "a dragon corrupted by millennia of hatred", l: "corrupted dragon"},
    {n: "a treacherous noble who made a pact with demons", l: "traitorous noble"},
    {n: "a witch who has been weaving her schemes in the shadows for centuries", l: "ancient witch"},
    {n: "a ruthless warlord leading an unstoppable horde", l: "warlord"},
    {n: "an ancient spirit that the land itself has rejected", l: "ancient spirit"},
    {n: "an entity that crossed over from beyond the veil of reality", l: "extradimensional entity"},
    {n: "a guild of assassins pulling the strings of power from the shadows", l: "dark guild"},
    {n: "a mad archmage convinced he can save the world by destroying it", l: "rogue archmage"},
    [{n: "a vampire lord who has enslaved an entire region", l: "vampire lord"}, 0.7],
    [{n: "a fallen goddess determined to reclaim her divinity at any cost", l: "fallen goddess"}, 0.5],
  ],
  minacce: [
    "is spreading a silent corruption that devours the land",
    "has shattered the balance between the living and the dead",
    "is gathering forces powerful enough to topple every known kingdom",
    "seeks an artifact whose rediscovery would bring the end of an age",
    "has already swallowed three cities in silence, and the silence is spreading",
    "manipulates the powerful from the dark, and no one knows who to trust",
    "is tearing open portals to planes of existence that should never touch this world",
    "has cursed the entire region: crops wither, wells run dry, and hope fades",
    "recruits the desperate and the outcast, promising power in exchange for blind devotion",
    "has stolen something sacred, and its absence is felt like an open wound in the world",
  ],
  hooks: [
    "You were hired — or perhaps you never had a choice",
    "Fate, misfortune, or perhaps both have led you here",
    "Someone you trusted asked this of you as a final favour",
    "You saw something you were never meant to see, and now you can't look away",
    "Your path and the threat's have crossed one too many times",
    "There is a debt to settle — of blood, of honour, or of gold",
    "A vision, a recurring dream, a prophecy: the place has haunted you for weeks",
    "You were in the wrong place at the wrong time — or perhaps the right one",
    "Someone you love is already in there",
    "You were told you are the only ones who can do this — maybe that's true",
  ],
  obiettivi: [
    {n: "defeat the antagonist before they complete their plan", l: "defeat the antagonist"},
    {n: "find and destroy the artifact that fuels their power", l: "destroy the artifact"},
    {n: "break the curse before it consumes everything", l: "break the curse"},
    {n: "uncover the truth behind the disappearances and end the terror", l: "investigation & resolution"},
    {n: "liberate the region and return it to its people", l: "liberate the territory"},
    {n: "recover something precious before it falls into the wrong hands", l: "recover the object"},
    {n: "close the portals and seal what was never meant to pass through", l: "dimensional seal"},
    {n: "survive, with as much truth in your pocket as possible", l: "survival & discovery"},
    {n: "forge an alliance between enemy factions before it's too late", l: "impossible diplomacy"},
    {n: "bring a buried history to light that someone has every interest in keeping hidden", l: "reveal the truth"},
  ],
  labels: { setting: 'Setting', antagonist: 'Antagonist', objective: 'Objective' },
};

// ═══════════════════════════════════════════════════════════════════════════════
// EXPORT
// ═══════════════════════════════════════════════════════════════════════════════

export function generateCampaign(locale = 'en') {
  const v = locale === 'it' ? it : en;

  const luogo = `${pick(v.luoghi)} ${pick(v.nomi)}`;
  const ant = pick(v.antagonisti);
  const minaccia = pick(v.minacce);
  const hook = pick(v.hooks);
  const amb = pick(v.ambientazioni);
  const obj = pick(v.obiettivi);

  return (
    `${luogo}, ${ant.n} ${minaccia}. ` +
    `${hook}.\n\n` +
    `${v.labels.setting}: ${amb}\n${v.labels.antagonist}: ${ant.l}\n${v.labels.objective}: ${obj.l}`
  );
}
