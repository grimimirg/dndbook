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

// ── LUOGHI ────────────────────────────────────────────────────────────────────

const prefissiLuogo = [
  'le antiche foreste di', 'le montagne spezzate di', 'le pianure desolate di',
  'le paludi silenziose di', 'le rovine sommerse di', 'i deserti ardenti di',
  'le isole nebbiose di', 'le catacombe dimenticate di', 'i porti oscuri di',
  'le valli proibite di', 'i boschi maledetti di', 'le scogliere battute dai venti di',
];

const nomiLuogo = [
  'Valdrath', 'Morthein', 'Caer Solenne', 'Duskmore', 'Aelundra',
  'Ferraspina', 'Cremora', 'Noctivale', 'Ironshard', 'Valthara',
  'Cinderhollow', 'Ombraluna', 'Greymantle', 'Fossatenebre', 'Aurenfall',
];

const tipiAmbientazione = [
  'foreste / natura selvaggia', 'montagne / rovine', 'città / intrighi di corte',
  'paludi / terre oscure', 'deserti / civiltà perdute', 'isole / mare aperto',
  'dungeon / catacombe', 'piani elementali', 'terre di frontiera',
];

// ── ANTAGONISTI {n: narrativo, l: etichetta} con peso opzionale ───────────────

const antagonisti = [
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
];

// ── MINACCE ───────────────────────────────────────────────────────────────────

const minacce = [
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
];

// ── HOOK ──────────────────────────────────────────────────────────────────────

const hooks = [
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
];

// ── OBIETTIVI {n: narrativo, l: etichetta} ────────────────────────────────────

const obiettivi = [
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
];

// ── EXPORT ────────────────────────────────────────────────────────────────────

export function generateCampaign() {
  const luogo = `${pick(prefissiLuogo)} ${pick(nomiLuogo)}`;
  const ambientazione = pick(tipiAmbientazione);
  const ant = pick(antagonisti);
  const minaccia = pick(minacce);
  const hook = pick(hooks);
  const obj = pick(obiettivi);

  return (
    `Nelle ${luogo}, ${ant.n} ${minaccia}. ` +
    `${hook}.\n\n` +
    `Ambientazione: ${ambientazione}\nAntagonista: ${ant.l}\nObiettivo: ${obj.l}`
  );
}
