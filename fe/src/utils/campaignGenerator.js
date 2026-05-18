// Weighted random pick. Items can be strings or [value, weight] pairs.
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

// ── ANTAGONISTI: [testo narrativo, etichetta, peso?] ─────────────────────────

const antagonisti = [
  ['un lich di potere inimmaginabile', 'lich antico'],
  ['un culto dedito al risveglio di un dio dimenticato', 'culto oscuro'],
  ['un drago corrotto dall\'odio millenario', 'drago corrotto'],
  ['un nobile traditore che ha stretto un patto con i demoni', 'nobile traditore'],
  ['una strega che tesse le sue trame da secoli nell\'ombra', 'strega millenaria'],
  ['un condottiero spietato alla guida di un\'orda inarrestabile', 'signore della guerra'],
  ['uno spirito antico che la terra stessa ha rigettato', 'spirito antico'],
  ['un\'entità venuta da oltre il velo della realtà', 'entità extradimensionale'],
  ['una gilda di assassini che muove i fili del potere dall\'ombra', 'gilda oscura'],
  ['un arcimago folle convinto di voler salvare il mondo distruggendolo', 'arcimago rinnegato'],
  [['un vampiro signore che ha assoggettato un\'intera regione', 'vampiro signore'], 0.7],
  [['una dea caduta che vuole riconquistare la sua divinità a qualsiasi costo', 'dea caduta'], 0.5],
];

// ── MINACCE ───────────────────────────────────────────────────────────────────

const minacce = [
  'sta diffondendo una corruzione silenziosa che divora la terra',
  'ha spezzato l\'equilibrio tra i vivi e i morti',
  'raduna forze abbastanza potenti da rovesciare ogni regno conosciuto',
  'cerca un artefatto la cui riscoperta porterebbe la fine di un\'era',
  'ha già fatto cadere tre città nel silenzio, e il silenzio avanza',
  'manipola i potenti dal buio, e nessuno sa ancora di chi fidarsi',
  'sta aprendo portali verso piani di esistenza che non dovrebbero toccare questo mondo',
  'ha posto una maledizione sull\'intera regione: i raccolti marciscono, i pozzi si prosciugano',
  'recluta disperati e reietti, promettendo potere in cambio di devozione cieca',
  'ha rubato qualcosa di sacro, e la sua assenza si sente come una ferita aperta nel mondo',
];

// ── HOOK ──────────────────────────────────────────────────────────────────────

const hooks = [
  'Siete stati ingaggiati — o forse non avete avuto altra scelta',
  'Il destino, la sfortuna, o forse entrambi vi hanno portato fin qui',
  'Qualcuno di cui vi fidavate vi ha chiesto questo come ultimo favore',
  'Avete visto qualcosa che non avreste dovuto vedere, e ora non potete più ignorarlo',
  'La vostra strada e quella della minaccia si sono incrociate una volta di troppo',
  'C\'è un debito da saldare — di sangue, di onore, o di oro',
  'Una visione, un sogno ricorrente, una profezia: il posto vi perseguita da settimane',
  'Eravate nel posto sbagliato al momento sbagliato — o forse quello giusto',
  'Qualcuno che amate è già là dentro',
  'Vi è stato detto che siete gli unici a poterlo fare — forse è vero, forse no',
];

// ── OBIETTIVI: [testo narrativo, etichetta] ───────────────────────────────────

const obiettivi = [
  ['sconfiggere l\'antagonista prima che completi il suo piano', 'sconfitta dell\'antagonista'],
  ['trovare e distruggere l\'artefatto che lo alimenta', 'distruzione dell\'artefatto'],
  ['spezzare la maledizione prima che divori tutto', 'rottura della maledizione'],
  ['scoprire la verità dietro le sparizioni e mettere fine al terrore', 'indagine e risoluzione'],
  ['liberare la regione dall\'occupazione e restituirla ai suoi abitanti', 'liberazione del territorio'],
  ['recuperare qualcosa di prezioso prima che cada nelle mani sbagliate', 'recupero dell\'oggetto'],
  ['chiudere i portali e sigillare ciò che non doveva passare', 'sigillo dimensionale'],
  ['sopravvivere, con quanta più verità in tasca possibile', 'sopravvivenza e scoperta'],
  ['trovare un\'alleanza tra fazioni nemiche prima che sia troppo tardi', 'diplomazia impossibile'],
  ['riportare alla luce una storia sepolta che qualcuno ha tutto l\'interesse a tenere nascosta', 'rivelazione della verità'],
];

// ── EXPORT ────────────────────────────────────────────────────────────────────

export function generateCampaign() {
  const luogo = `${pick(prefissiLuogo)} **${pick(nomiLuogo)}**`;
  const ambientazione = pick(tipiAmbientazione);

  // antagonisti con peso opzionale: voce è [testo, label] o [[testo, label], peso]
  const antRaw = pick(antagonisti);
  const [antNarr, antLabel] = Array.isArray(antRaw[0]) ? antRaw[0] : antRaw;

  const minaccia = pick(minacce);
  const hook = pick(hooks);

  const [objNarr, objLabel] = pick(obiettivi);

  return (
    `Nelle ${luogo}, ${antNarr} ${minaccia}. ` +
    `${hook}.\n\n` +
    `**Ambientazione:** ${ambientazione} · **Antagonista:** ${antLabel} · **Obiettivo:** ${objLabel}`
  );
}
