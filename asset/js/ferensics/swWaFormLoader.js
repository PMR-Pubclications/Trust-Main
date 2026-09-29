const fs = require('fs');
const { parseStringPromise } = require('xml2js');

async function processSWWaForm(xmlFilePath) {
  const xmlData = fs.readFileSync(xmlFilePath, 'utf8');
  const parsed = await parseStringPromise(xmlData, { explicitArray: false });

  const form = parsed.SWWA_JurisdictionalForm;
  const jur = form.Jurisdiction;
  const meta = form.FormMetadata;

  console.log(`\n==================================================`);
  console.log(`[SW WA FORM INGESTION] ${jur.County} County, WA`);
  console.log(`Agency: ${jur.AgencyName} (${jur.AgencyCategory})`);
  console.log(`Form ID: ${meta.FormID} | Title: ${meta.FormTitle}`);
  console.log(`Statute Ref: ${meta.StatuteOrOrdinance}`);
  console.log(`Operator ID: ${form.VerificationBlock.OperatorID}`);
  console.log(`Signature Hash: ${form.VerificationBlock.SignatureHash}`);
  console.log(`==================================================\n`);

  // Target routing based on county
  switch (jur.County) {
    case 'Clark':
      routeClarkCountyData(form.Payload);
      break;
    case 'Skamania':
      routeSkamaniaCountyData(form.Payload);
      break;
    case 'Cowlitz':
      routeCowlitzCountyData(form.Payload);
      break;
  }
}

function routeClarkCountyData(payload) {
  console.log('>> Routing to CRESA / Clark County Superior Court database pipeline...');
}

function routeSkamaniaCountyData(payload) {
  console.log('>> Routing to Skamania SAR / VHF Emergency pipeline...');
}

function routeCowlitzCountyData(payload) {
  console.log('>> Routing to Hall of Justice / Cowlitz 911 pipeline...');
}

module.exports = { processSWWaForm };
