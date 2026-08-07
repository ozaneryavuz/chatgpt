(function(){
  'use strict';

  function ready(callback){
    if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',callback,{once:true});
    else callback();
  }

  function asciiName(value){
    return String(value||'')
      .replace(/İ/g,'I').replace(/ı/g,'i').replace(/Ç/g,'C').replace(/ç/g,'c')
      .replace(/Ğ/g,'G').replace(/ğ/g,'g').replace(/Ö/g,'O').replace(/ö/g,'o')
      .replace(/Ş/g,'S').replace(/ş/g,'s').replace(/Ü/g,'U').replace(/ü/g,'u')
      .normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  }

  ready(function(){
    const api=window.Alo186Companies;
    const provinceSelect=document.getElementById('provinceSelect');
    const districtField=document.getElementById('districtField');
    const districtSelect=document.getElementById('districtSelect');
    const result=document.getElementById('companyResult');
    const resultTitle=document.getElementById('resultTitle');
    const resultText=document.getElementById('resultText');
    const resultGuide=document.getElementById('resultGuide');
    const resultStatus=document.getElementById('finderStatus');
    const quickButtons=Array.from(document.querySelectorAll('[data-province-id]'));

    if(!provinceSelect||!districtField||!districtSelect||!result||!resultTitle||!resultText||!resultGuide||!resultStatus)return;
    if(!api){
      resultStatus.textContent='The local company dataset could not be loaded. Use the directory below or call 186.';
      return;
    }

    const provinces=Object.entries(api.provinceNames)
      .map(function(entry){return{id:Number(entry[0]),name:entry[1]};})
      .sort(function(a,b){return asciiName(a.name).localeCompare(asciiName(b.name),'en');});

    provinces.forEach(function(province){
      const option=document.createElement('option');
      const ascii=asciiName(province.name);
      option.value=String(province.id);
      option.textContent=ascii===province.name?province.name:province.name+' / '+ascii;
      provinceSelect.appendChild(option);
    });

    function appendDistrictGroup(label,names){
      const group=document.createElement('optgroup');
      group.label=label;
      names.forEach(function(name){
        const option=document.createElement('option');
        option.value=name;
        option.textContent=name+' / '+asciiName(name);
        group.appendChild(option);
      });
      districtSelect.appendChild(group);
    }

    appendDistrictGroup('European side — BEDAŞ',api.istanbulEurope);
    appendDistrictGroup('Asian side — AYEDAŞ',api.istanbulAsia);

    function clearResult(message){
      result.hidden=true;
      resultTitle.textContent='';
      resultText.textContent='';
      resultGuide.removeAttribute('href');
      resultStatus.textContent=message||'';
    }

    function renderCompany(company,province,district){
      if(!company){
        clearResult('Select an Istanbul district to resolve BEDAŞ or AYEDAŞ.');
        return;
      }
      const location=district?district+', '+province.name:province.name;
      resultTitle.textContent=company.name+' ('+company.code+')';
      resultText.textContent=company.name+' is the electricity distribution company mapped to '+location+'. For a public-grid outage or street-lighting fault, use 186 or the company’s verified official channel.';
      resultGuide.href=api.companyUrl(company);
      resultGuide.textContent='Open the verified contact guide in Turkish →';
      result.hidden=false;
      resultStatus.textContent='Match found for '+location+'. No personal data was used.';
      result.focus({preventScroll:true});
    }

    function selectedProvince(){
      const id=Number(provinceSelect.value);
      return provinces.find(function(item){return item.id===id;})||null;
    }

    function updateFromProvince(){
      const province=selectedProvince();
      districtSelect.value='';
      if(!province){
        districtField.classList.add('hidden');
        clearResult('Choose a province to find the responsible company.');
        return;
      }
      if(province.id===34){
        districtField.classList.remove('hidden');
        clearResult('Istanbul has two distribution regions. Choose the district or side.');
        districtSelect.focus({preventScroll:true});
        return;
      }
      districtField.classList.add('hidden');
      renderCompany(api.companyForProvince(province.id),province,'');
    }

    provinceSelect.addEventListener('change',updateFromProvince);
    districtSelect.addEventListener('change',function(){
      const province=selectedProvince();
      if(!province||province.id!==34)return;
      const district=districtSelect.value;
      renderCompany(api.companyForProvince(34,district),province,district);
    });

    quickButtons.forEach(function(button){
      button.addEventListener('click',function(){
        provinceSelect.value=button.getAttribute('data-province-id')||'';
        updateFromProvince();
        document.getElementById('finder').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
      });
    });

    clearResult('Choose a province to find the responsible company.');
  });
})();
