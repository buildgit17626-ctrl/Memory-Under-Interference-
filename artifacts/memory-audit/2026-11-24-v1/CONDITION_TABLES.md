# Per-condition audit table

Attempt-weighted rates use valid-input correctness denominators; API/infrastructure failures remain separate. Caps are bounded-endpoint nonpasses. Full CIs, all timing fields and numerators/denominators are in conditions.json/csv. M1 correctness here is the focal target; whole-bundle/per-function endpoints are separate.

Energy tool/mode: HWiNFO CPU Package Power; trapezoidal; approximate post-load; block-start net.

|Stage/model|Condition|Attempts|Correct/usable|Pass %|95% task CI %|Caps|Energy n|Mean input/output tokens|Gross/net Wh total|Net Wh/correct|
|---|---|---:|---|---:|---|---:|---:|---|---|---:|
|E0/qwen2.5-coder:0.5b|P1|492|234/490|47.76|[40.65, 54.47]|3|490|164.2/220|23.52/19.4|0.08291|
|E0/qwen2.5-coder:0.5b|P3_1|492|223/492|45.33|[38.82, 52.03]|3|492|210.2/364.3|39.81/32.98|0.1479|
|E0/qwen2.5-coder:1.5b|P1|492|293/492|59.55|[52.44, 66.46]|0|492|164.2/74.09|20.62/17.08|0.05829|
|E0/qwen2.5-coder:1.5b|P3_1|492|306/492|62.2|[55.69, 69.11]|0|492|210.2/128.7|35.07/29.27|0.09566|
|E4_original_pilot/qwen2.5-coder:0.5b|cold/prefix1000|1|None/0|NA|unavailable|0|1|1055/64|0.05526/0.04683|NA|
|E4_original_pilot/qwen2.5-coder:0.5b|cold/prefix2000|1|None/0|NA|unavailable|0|1|2055/64|0.1048/0.0885|NA|
|E4_original_pilot/qwen2.5-coder:0.5b|warm/prefix0|1|None/0|NA|unavailable|0|1|54/64|0.008322/0.006575|NA|
|E4_original_pilot/qwen2.5-coder:0.5b|warm/prefix2000|1|None/0|NA|unavailable|0|1|2055/64|0.009624/0.007248|NA|
|E4_original_pilot/qwen2.5-coder:0.5b|warm/prefix4000|1|None/0|NA|unavailable|0|1|4055/19|0.003703/0.00249|NA|
|E4_original_pilot/qwen2.5-coder:1.5b|cold/prefix0|1|None/0|NA|unavailable|0|1|54/64|0.03037/0.02592|NA|
|E4_original_pilot/qwen2.5-coder:1.5b|cold/prefix2000|1|None/0|NA|unavailable|0|1|2055/64|0.1563/0.1331|NA|
|E4_original_pilot/qwen2.5-coder:1.5b|warm/prefix0|1|None/0|NA|unavailable|0|1|54/64|0.02428/0.02012|NA|
|E4_original_pilot/qwen2.5-coder:1.5b|warm/prefix2000|1|None/0|NA|unavailable|0|1|2055/64|0.04038/0.03489|NA|
|E4_original_pilot/qwen2.5-coder:1.5b|warm/prefix4000|1|None/0|NA|unavailable|0|1|4055/64|0.03674/0.03042|NA|
|E4_partial/qwen2.5-coder:0.5b|cold/prefix0|4|None/0|NA|unavailable|0|4|57/64|0.02788/0.01787|NA|
|E4_partial/qwen2.5-coder:0.5b|cold/prefix1000|4|None/0|NA|unavailable|0|4|1058/64|0.206/0.1617|NA|
|E4_partial/qwen2.5-coder:0.5b|cold/prefix2000|6|None/0|NA|unavailable|0|6|2058/64|0.6182/0.4946|NA|
|E4_partial/qwen2.5-coder:0.5b|cold/prefix4000|2|None/0|NA|unavailable|0|2|4058/64|0.4028/0.318|NA|
|E4_partial/qwen2.5-coder:0.5b|cold/prefix500|5|None/0|NA|unavailable|0|5|558/64|0.1439/0.1098|NA|
|E4_partial/qwen2.5-coder:0.5b|warm/prefix0|4|None/0|NA|unavailable|0|4|57/64|0.02102/0.01259|NA|
|E4_partial/qwen2.5-coder:0.5b|warm/prefix1000|5|None/0|NA|unavailable|0|5|1058/64|0.03854/0.02504|NA|
|E4_partial/qwen2.5-coder:0.5b|warm/prefix2000|4|None/0|NA|unavailable|0|4|2058/64|0.03686/0.02488|NA|
|E4_partial/qwen2.5-coder:0.5b|warm/prefix4000|6|None/0|NA|unavailable|0|6|4058/64|0.1015/0.07395|NA|
|E4_partial/qwen2.5-coder:0.5b|warm/prefix500|2|None/0|NA|unavailable|0|2|558/64|0.01215/0.007446|NA|
|E4_partial/qwen2.5-coder:1.5b|cold/prefix0|2|None/0|NA|unavailable|0|2|57/64|0.04826/0.03736|NA|
|E4_partial/qwen2.5-coder:1.5b|cold/prefix1000|3|None/0|NA|unavailable|0|3|1058/64|0.235/0.1839|NA|
|E4_partial/qwen2.5-coder:1.5b|cold/prefix2000|2|None/0|NA|unavailable|0|2|2058/64|0.2975/0.2361|NA|
|E4_partial/qwen2.5-coder:1.5b|cold/prefix4000|5|None/0|NA|unavailable|0|5|4058/64|1.367/1.04|NA|
|E4_partial/qwen2.5-coder:1.5b|cold/prefix500|2|None/0|NA|unavailable|0|2|558/64|0.08986/0.06686|NA|
|E4_partial/qwen2.5-coder:1.5b|warm/prefix0|1|None/0|NA|unavailable|0|1|57/64|0.02302/0.018|NA|
|E4_partial/qwen2.5-coder:1.5b|warm/prefix1000|4|None/0|NA|unavailable|0|4|1058/64|0.09587/0.07287|NA|
|E4_partial/qwen2.5-coder:1.5b|warm/prefix2000|4|None/0|NA|unavailable|0|4|2058/64|0.1072/0.08127|NA|
|E4_partial/qwen2.5-coder:1.5b|warm/prefix4000|7|None/0|NA|unavailable|0|7|4058/64|0.2201/0.1653|NA|
|E4_partial/qwen2.5-coder:1.5b|warm/prefix500|4|None/0|NA|unavailable|0|4|558/64|0.1/0.07854|NA|
|E4_schema_pilot/qwen2.5-coder:0.5b|cold/prefix0|1|None/0|NA|unavailable|0|1|57/64|0.0106/0.007666|NA|
|E4_schema_pilot/qwen2.5-coder:0.5b|cold/prefix1000|1|None/0|NA|unavailable|0|1|1058/64|0.04954/0.03531|NA|
|E4_schema_pilot/qwen2.5-coder:0.5b|cold/prefix2000|1|None/0|NA|unavailable|0|1|2058/64|0.1021/0.07569|NA|
|E4_schema_pilot/qwen2.5-coder:0.5b|cold/prefix4000|1|None/0|NA|unavailable|0|1|4058/64|0.1848/0.1239|NA|
|E4_schema_pilot/qwen2.5-coder:0.5b|cold/prefix500|1|None/0|NA|unavailable|0|1|558/64|0.02511/0.01645|NA|
|E4_schema_pilot/qwen2.5-coder:0.5b|warm/prefix0|1|None/0|NA|unavailable|0|1|57/64|0.006507/0.003949|NA|
|E4_schema_pilot/qwen2.5-coder:0.5b|warm/prefix1000|1|None/0|NA|unavailable|0|1|1058/64|0.01064/0.007361|NA|
|E4_schema_pilot/qwen2.5-coder:0.5b|warm/prefix2000|1|None/0|NA|unavailable|0|1|2058/64|0.01234/0.008109|NA|
|E4_schema_pilot/qwen2.5-coder:0.5b|warm/prefix4000|1|None/0|NA|unavailable|0|1|4058/64|0.01782/0.01179|NA|
|E4_schema_pilot/qwen2.5-coder:0.5b|warm/prefix500|1|None/0|NA|unavailable|0|1|558/64|0.01273/0.009245|NA|
|E4_schema_pilot/qwen2.5-coder:1.5b|cold/prefix0|1|None/0|NA|unavailable|0|1|57/64|0.02085/0.01421|NA|
|E4_schema_pilot/qwen2.5-coder:1.5b|cold/prefix1000|1|None/0|NA|unavailable|0|1|1058/64|0.07179/0.04932|NA|
|E4_schema_pilot/qwen2.5-coder:1.5b|cold/prefix2000|1|None/0|NA|unavailable|0|1|2058/64|0.1256/0.08471|NA|
|E4_schema_pilot/qwen2.5-coder:1.5b|cold/prefix4000|1|None/0|NA|unavailable|0|1|4058/64|0.2683/0.1825|NA|
|E4_schema_pilot/qwen2.5-coder:1.5b|cold/prefix500|1|None/0|NA|unavailable|0|1|558/64|0.04719/0.0324|NA|
|E4_schema_pilot/qwen2.5-coder:1.5b|warm/prefix0|1|None/0|NA|unavailable|0|1|57/64|0.0191/0.01314|NA|
|E4_schema_pilot/qwen2.5-coder:1.5b|warm/prefix1000|1|None/0|NA|unavailable|0|1|1058/64|0.02245/0.01542|NA|
|E4_schema_pilot/qwen2.5-coder:1.5b|warm/prefix2000|1|None/0|NA|unavailable|0|1|2058/64|0.02508/0.01709|NA|
|E4_schema_pilot/qwen2.5-coder:1.5b|warm/prefix4000|1|None/0|NA|unavailable|0|1|4058/64|0.03055/0.02078|NA|
|E4_schema_pilot/qwen2.5-coder:1.5b|warm/prefix500|1|None/0|NA|unavailable|0|1|558/64|0.0211/0.01457|NA|
|E5/qwen2.5-coder:0.5b|buried|40|15/40|37.5|[22.5, 52.5]|1|40|1333/265.6|4.882/3.807|0.2538|
|E5/qwen2.5-coder:0.5b|corrected|40|14/40|35|[20, 50]|2|40|1357/333.2|5.587/4.387|0.3133|
|E5/qwen2.5-coder:0.5b|immediate|40|11/40|27.5|[15, 42.5]|2|40|1333/355.7|5.814/4.526|0.4114|
|E5/qwen2.5-coder:0.5b|no_preference|40|14/40|35|[20, 50]|3|40|1315/398.2|6.143/4.837|0.3455|
|E5/qwen2.5-coder:0.5b|replayed|40|13/40|32.5|[17.5, 47.5]|0|40|1351/205|4.363/3.438|0.2645|
|E5/qwen2.5-coder:1.5b|buried|40|21/40|52.5|[37.5, 67.5]|0|40|1333/62.83|4.597/3.575|0.1703|
|E5/qwen2.5-coder:1.5b|corrected|40|22/40|55|[40, 70]|0|40|1357/78.5|4.996/3.913|0.1778|
|E5/qwen2.5-coder:1.5b|immediate|40|23/40|57.5|[42.5, 72.5]|0|40|1333/64.95|4.687/3.659|0.1591|
|E5/qwen2.5-coder:1.5b|no_preference|40|25/40|62.5|[47.5, 77.5]|0|40|1315/201.9|7.524/5.928|0.2371|
|E5/qwen2.5-coder:1.5b|replayed|40|23/40|57.5|[42.5, 72.5]|0|40|1351/64.8|4.642/3.616|0.1572|
|E5_pilot/qwen2.5-coder:0.5b|buried|5|1/5|20|[0, 60]|0|5|1367/260.2|0.637/0.4499|0.4499|
|E5_pilot/qwen2.5-coder:0.5b|corrected|5|0/5|0|[0, 0]|0|5|1391/222.2|0.567/0.4081|NA|
|E5_pilot/qwen2.5-coder:0.5b|immediate|5|0/5|0|[0, 0]|0|5|1367/213.4|0.5484/0.3938|NA|
|E5_pilot/qwen2.5-coder:0.5b|no_preference|5|0/5|0|[0, 0]|0|5|1349/268.2|0.6115/0.4315|NA|
|E5_pilot/qwen2.5-coder:0.5b|replayed|5|0/5|0|[0, 0]|0|5|1385/207|0.5401/0.3866|NA|
|E5_pilot/qwen2.5-coder:1.5b|buried|5|2/5|40|[0, 80]|0|5|1367/73.6|0.6188/0.4359|0.218|
|E5_pilot/qwen2.5-coder:1.5b|corrected|5|2/5|40|[0, 80]|0|5|1391/73.6|0.6211/0.4498|0.2249|
|E5_pilot/qwen2.5-coder:1.5b|immediate|5|2/5|40|[0, 80]|0|5|1367/63.6|0.5876/0.4307|0.2154|
|E5_pilot/qwen2.5-coder:1.5b|no_preference|5|3/5|60|[20, 100]|0|5|1349/256.8|1.091/0.7576|0.2525|
|E5_pilot/qwen2.5-coder:1.5b|replayed|5|2/5|40|[0, 80]|0|5|1385/73.8|0.6226/0.4301|0.2151|
|M1/qwen2.5-coder:0.5b|active/K2|40|8/40|20|[10, 32.5]|1|40|301.9/437.1|3.628/2.624|0.328|
|M1/qwen2.5-coder:0.5b|active/K3|40|3/40|7.5|[0, 17.5]|1|40|437.8/608|5.359/4.065|1.355|
|M1/qwen2.5-coder:0.5b|active/K4|40|3/40|7.5|[0, 17.5]|0|40|573.6/584.4|5.094/3.9|1.3|
|M1/qwen2.5-coder:0.5b|active/K6|40|2/40|5|[0, 12.5]|3|40|845.4/1729|18.75/14.19|7.094|
|M1/qwen2.5-coder:0.5b|filler/K2|40|17/40|42.5|[27.5, 57.5]|0|40|311.6/215.8|1.982/1.492|0.08774|
|M1/qwen2.5-coder:0.5b|filler/K3|40|20/40|50|[35, 65]|0|40|450.6/220.3|2.202/1.661|0.08305|
|M1/qwen2.5-coder:0.5b|filler/K4|40|18/40|45|[30, 60]|1|40|589.6/256|2.756/2.062|0.1146|
|M1/qwen2.5-coder:0.5b|filler/K6|40|18/40|45|[30, 60]|0|40|867.7/213.4|2.96/2.252|0.1251|
|M1/qwen2.5-coder:0.5b|isolated|40|15/40|37.5|[22.5, 52.5]|0|40|172.6/193.4|1.554/1.199|0.07992|
|M1/qwen2.5-coder:0.5b|passive/K2|40|12/40|30|[15, 45]|0|40|311.6/243.6|2.134/1.647|0.1372|
|M1/qwen2.5-coder:0.5b|passive/K3|40|11/40|27.5|[15, 42.5]|2|40|450.6/422.9|3.724/2.76|0.251|
|M1/qwen2.5-coder:0.5b|passive/K4|40|9/40|22.5|[10, 35]|1|40|589.6/478.7|4.369/3.305|0.3672|
|M1/qwen2.5-coder:0.5b|passive/K6|40|8/40|20|[7.5, 32.5]|1|40|867.7/493.7|4.975/3.738|0.4672|
|M1/qwen2.5-coder:1.5b|active/K2|40|20/40|50|[35, 65]|0|40|301.9/108.7|2.448/1.884|0.09419|
|M1/qwen2.5-coder:1.5b|active/K3|40|17/40|42.5|[27.5, 57.5]|0|40|437.8/170.2|3.784/2.936|0.1727|
|M1/qwen2.5-coder:1.5b|active/K4|40|16/40|40|[25, 55]|0|40|573.6/211.7|4.756/3.7|0.2313|
|M1/qwen2.5-coder:1.5b|active/K6|40|15/40|37.5|[22.5, 52.5]|0|40|845.4/322.1|7.476/5.711|0.3807|
|M1/qwen2.5-coder:1.5b|filler/K2|40|28/40|70|[55, 85]|0|40|311.6/124.4|2.79/2.143|0.07654|
|M1/qwen2.5-coder:1.5b|filler/K3|40|29/40|72.5|[57.5, 85]|0|40|450.6/125.6|3.117/2.399|0.08272|
|M1/qwen2.5-coder:1.5b|filler/K4|40|29/40|72.5|[57.5, 85]|0|40|589.6/131.1|3.513/2.691|0.0928|
|M1/qwen2.5-coder:1.5b|filler/K6|40|28/40|70|[55, 82.5]|0|40|867.7/125.8|4.046/3.067|0.1095|
|M1/qwen2.5-coder:1.5b|isolated|40|28/40|70|[55, 85]|0|40|172.6/97.35|1.975/1.524|0.05441|
|M1/qwen2.5-coder:1.5b|passive/K2|40|24/40|60|[45, 75]|0|40|311.6/144|3.119/2.372|0.09884|
|M1/qwen2.5-coder:1.5b|passive/K3|40|21/40|52.5|[37.5, 67.5]|0|40|450.6/185.4|4.115/3.156|0.1503|
|M1/qwen2.5-coder:1.5b|passive/K4|40|21/40|52.5|[37.5, 67.5]|1|40|589.6/243.1|5.432/4.039|0.1923|
|M1/qwen2.5-coder:1.5b|passive/K6|40|22/40|55|[40, 70]|0|40|867.7/254.5|6.283/4.732|0.2151|
|M1_pilot/qwen2.5-coder:0.5b|active/K2|5|0/5|0|[0, 0]|0|5|409.6/612.4|0.6218/0.4288|NA|
|M1_pilot/qwen2.5-coder:0.5b|active/K4|5|0/5|0|[0, 0]|0|5|667.6/681.4|0.7587/0.5188|NA|
|M1_pilot/qwen2.5-coder:0.5b|filler/K2|5|2/5|40|[0, 80]|0|5|419.2/386|0.4213/0.274|0.137|
|M1_pilot/qwen2.5-coder:0.5b|filler/K4|5|2/5|40|[0, 80]|0|5|683.8/361.4|0.4708/0.3103|0.1552|
|M1_pilot/qwen2.5-coder:0.5b|isolated|5|2/5|40|[0, 80]|0|5|225.8/321.6|0.3186/0.2218|0.1109|
|M1_pilot/qwen2.5-coder:0.5b|passive/K2|5|0/5|0|[0, 0]|0|5|419.2/377.8|0.4161/0.2786|NA|
|M1_pilot/qwen2.5-coder:0.5b|passive/K4|5|0/5|0|[0, 0]|0|5|683.8/592.6|0.6633/0.4355|NA|
|M1_pilot/qwen2.5-coder:1.5b|active/K2|5|1/5|20|[0, 60]|0|5|409.6/128.2|0.4018/0.2837|0.2837|
|M1_pilot/qwen2.5-coder:1.5b|active/K4|5|1/5|20|[0, 60]|0|5|667.6/234.6|0.704/0.4926|0.4926|
|M1_pilot/qwen2.5-coder:1.5b|filler/K2|5|4/5|80|[40, 100]|0|5|419.2/171|0.4932/0.3378|0.08444|
|M1_pilot/qwen2.5-coder:1.5b|filler/K4|5|4/5|80|[40, 100]|0|5|683.8/171.2|0.5605/0.4049|0.1012|
|M1_pilot/qwen2.5-coder:1.5b|isolated|5|4/5|80|[40, 100]|0|5|225.8/159.6|0.4021/0.2925|0.07313|
|M1_pilot/qwen2.5-coder:1.5b|passive/K2|5|2/5|40|[0, 80]|0|5|419.2/291.2|0.7112/0.4745|0.2372|
|M1_pilot/qwen2.5-coder:1.5b|passive/K4|5|2/5|40|[0, 80]|0|5|683.8/496.8|1.266/0.8591|0.4296|
|M2/qwen2.5-coder:0.5b|isolated|40|15/40|37.5|[22.5, 52.5]|0|40|200.6/200.6|1.695/1.428|0.09522|
|M2/qwen2.5-coder:0.5b|neutral|40|14/40|35|[20, 50]|0|40|1769/191.8|4.741/3.985|0.2847|
|M2/qwen2.5-coder:0.5b|other_one|40|11/40|27.5|[15, 42.5]|0|40|1769/184.4|4.647/3.901|0.3546|
|M2/qwen2.5-coder:0.5b|other_three|40|12/40|30|[17.5, 45]|0|40|1769/215.7|4.929/4.143|0.3452|
|M2/qwen2.5-coder:0.5b|similar|40|9/40|22.5|[10, 37.5]|1|40|1769/198.5|4.801/4.029|0.4476|
|M2/qwen2.5-coder:1.5b|isolated|40|25/40|62.5|[47.5, 77.5]|0|40|200.6/90.53|1.968/1.671|0.06682|
|M2/qwen2.5-coder:1.5b|neutral|40|25/40|62.5|[45, 77.5]|0|40|1769/99|6.043/5.08|0.2032|
|M2/qwen2.5-coder:1.5b|other_one|40|26/40|65|[50, 80]|0|40|1769/102.7|6.052/5.079|0.1953|
|M2/qwen2.5-coder:1.5b|other_three|40|19/40|47.5|[32.5, 62.5]|0|40|1769/91.95|5.957/5.031|0.2648|
|M2/qwen2.5-coder:1.5b|similar|40|24/40|60|[45, 75]|0|40|1769/105.5|6.22/5.249|0.2187|
|M2_pilot/qwen2.5-coder:0.5b|isolated|5|1/5|20|[0, 60]|0|5|199.6/179|0.1994/0.1672|0.1672|
|M2_pilot/qwen2.5-coder:0.5b|neutral|5|1/5|20|[0, 60]|0|5|1768/171.2|0.5666/0.4699|0.4699|
|M2_pilot/qwen2.5-coder:0.5b|other_one|5|1/5|20|[0, 60]|0|5|1768/182|0.5834/0.4829|0.4829|
|M2_pilot/qwen2.5-coder:0.5b|other_three|5|1/5|20|[0, 60]|0|5|1768/198.2|0.6051/0.5078|0.5078|
|M2_pilot/qwen2.5-coder:0.5b|similar|5|1/5|20|[0, 60]|0|5|1768/143.8|0.5582/0.4688|0.4688|
|M2_pilot/qwen2.5-coder:1.5b|isolated|5|3/5|60|[20, 100]|0|5|199.6/78.8|0.2283/0.1925|0.06416|
|M2_pilot/qwen2.5-coder:1.5b|neutral|5|2/5|40|[0, 80]|0|5|1768/96.8|0.7658/0.6379|0.3189|
|M2_pilot/qwen2.5-coder:1.5b|other_one|5|3/5|60|[20, 100]|0|5|1768/95.2|0.7387/0.6124|0.2041|
|M2_pilot/qwen2.5-coder:1.5b|other_three|5|1/5|20|[0, 60]|0|5|1768/74|0.6928/0.5761|0.5761|
|M2_pilot/qwen2.5-coder:1.5b|similar|5|2/5|40|[0, 80]|0|5|1768/98.6|0.7571/0.6304|0.3152|
|M3R2/qwen2.5-coder:0.5b|irrelevant_1000_beginning|40|15/40|37.5|[22.5, 52.5]|0|40|1199/194.4|3.639/2.853|0.1902|
|M3R2/qwen2.5-coder:0.5b|irrelevant_1000_end|40|19/40|47.5|[32.5, 62.5]|0|40|1199/212.8|3.741/2.911|0.1532|
|M3R2/qwen2.5-coder:0.5b|irrelevant_2000_beginning|40|15/40|37.5|[22.5, 52.5]|0|40|2199/192.4|5.565/4.287|0.2858|
|M3R2/qwen2.5-coder:0.5b|irrelevant_2000_end|40|17/40|42.5|[27.5, 57.5]|0|40|2199/204.5|5.77/4.546|0.2674|
|M3R2/qwen2.5-coder:0.5b|isolated|40|18/40|45|[30, 60]|0|40|198.1/212.1|1.837/1.455|0.08081|
|M3R2/qwen2.5-coder:0.5b|near_duplicate_1000_beginning|40|13/40|32.5|[20, 47.5]|0|40|1199/197.9|3.614/2.802|0.2156|
|M3R2/qwen2.5-coder:0.5b|near_duplicate_1000_end|40|13/40|32.5|[20, 47.5]|0|40|1199/159.6|3.393/2.692|0.2071|
|M3R2/qwen2.5-coder:0.5b|near_duplicate_2000_beginning|40|10/40|25|[12.5, 37.5]|0|40|2199/175.7|5.525/4.285|0.4285|
|M3R2/qwen2.5-coder:0.5b|near_duplicate_2000_end|40|12/40|30|[17.5, 45]|0|40|2199/181.9|5.629/4.443|0.3702|
|M3R2/qwen2.5-coder:0.5b|related_1000_beginning|40|10/39|25.64|[12.82, 38.53]|0|39|1200/195.4|3.513/2.738|0.2738|
|M3R2/qwen2.5-coder:0.5b|related_1000_end|40|12/40|30|[17.5, 42.56]|0|40|1199/201.2|3.705/2.917|0.2431|
|M3R2/qwen2.5-coder:0.5b|related_2000_beginning|40|12/40|30|[17.5, 45]|0|40|2199/197.9|5.7/4.411|0.3676|
|M3R2/qwen2.5-coder:0.5b|related_2000_end|40|13/40|32.5|[17.5, 47.5]|1|40|2199/238.8|6.097/4.784|0.368|
|M3R2/qwen2.5-coder:1.5b|irrelevant_1000_beginning|40|25/40|62.5|[47.5, 77.5]|1|40|1199/170.9|5.997/4.666|0.1866|
|M3R2/qwen2.5-coder:1.5b|irrelevant_1000_end|40|27/40|67.5|[52.5, 82.5]|1|40|1199/213.4|6.775/5.311|0.1967|
|M3R2/qwen2.5-coder:1.5b|irrelevant_2000_beginning|40|26/40|65|[50, 80]|1|40|2199/159.3|8.661/6.756|0.2598|
|M3R2/qwen2.5-coder:1.5b|irrelevant_2000_end|40|26/40|65|[50, 80]|0|40|2199/170.6|8.857/6.841|0.2631|
|M3R2/qwen2.5-coder:1.5b|isolated|40|24/40|60|[45, 75]|1|40|198.1/137.2|2.898/2.316|0.09651|
|M3R2/qwen2.5-coder:1.5b|near_duplicate_1000_beginning|40|24/40|60|[45, 75]|0|40|1199/152.9|5.64/4.427|0.1844|
|M3R2/qwen2.5-coder:1.5b|near_duplicate_1000_end|40|26/40|65|[50, 80]|1|40|1199/205.2|6.677/5.309|0.2042|
|M3R2/qwen2.5-coder:1.5b|near_duplicate_2000_beginning|40|25/40|62.5|[47.5, 77.5]|1|39|2199/170.1|8.493/6.604|0.2752|
|M3R2/qwen2.5-coder:1.5b|near_duplicate_2000_end|40|25/40|62.5|[47.5, 75]|1|40|2199/200.3|9.491/7.464|0.2986|
|M3R2/qwen2.5-coder:1.5b|related_1000_beginning|40|25/40|62.5|[47.5, 77.5]|1|40|1199/194.3|6.369/4.955|0.1982|
|M3R2/qwen2.5-coder:1.5b|related_1000_end|40|26/40|65|[50, 80]|0|40|1199/125.4|5.073/4.02|0.1546|
|M3R2/qwen2.5-coder:1.5b|related_2000_beginning|40|22/40|55|[40, 70]|1|40|2199/192.3|9.069/7.006|0.3184|
|M3R2/qwen2.5-coder:1.5b|related_2000_end|40|26/40|65|[50, 80]|0|40|2199/110.2|7.6/5.947|0.2287|
|M3R2_pilot/qwen2.5-coder:0.5b|irrelevant_1000_beginning|5|1/5|20|[0, 60]|0|5|1206/212.6|0.4958/0.4039|0.4039|
|M3R2_pilot/qwen2.5-coder:0.5b|irrelevant_1000_end|5|1/5|20|[0, 60]|0|5|1206/227.2|0.5278/0.4364|0.4364|
|M3R2_pilot/qwen2.5-coder:0.5b|irrelevant_2000_beginning|5|1/5|20|[0, 60]|0|5|2206/199.4|0.7441/0.6033|0.6033|
|M3R2_pilot/qwen2.5-coder:0.5b|irrelevant_2000_end|5|1/5|20|[0, 60]|0|5|2206/215.6|0.7949/0.653|0.653|
|M3R2_pilot/qwen2.5-coder:0.5b|isolated|5|2/5|40|[0, 80]|0|5|205.4/234|0.2686/0.2214|0.1107|
|M3R2_pilot/qwen2.5-coder:0.5b|near_duplicate_1000_beginning|5|1/5|20|[0, 60]|0|5|1206/175.4|0.4604/0.3778|0.3778|
|M3R2_pilot/qwen2.5-coder:0.5b|near_duplicate_1000_end|5|2/5|40|[0, 80]|0|5|1206/125.4|0.3934/0.319|0.1595|
|M3R2_pilot/qwen2.5-coder:0.5b|near_duplicate_2000_beginning|5|1/5|20|[0, 60]|0|5|2206/178.8|0.7161/0.5771|0.5771|
|M3R2_pilot/qwen2.5-coder:0.5b|near_duplicate_2000_end|5|1/5|20|[0, 60]|0|5|2206/197.4|0.7499/0.6096|0.6096|
|M3R2_pilot/qwen2.5-coder:0.5b|related_1000_beginning|5|1/5|20|[0, 60]|0|5|1206/174.8|0.4577/0.3756|0.3756|
|M3R2_pilot/qwen2.5-coder:0.5b|related_1000_end|5|1/5|20|[0, 60]|0|5|1206/211.4|0.4983/0.4064|0.4064|
|M3R2_pilot/qwen2.5-coder:0.5b|related_2000_beginning|5|1/5|20|[0, 60]|0|5|2206/196|0.7479/0.6089|0.6089|
|M3R2_pilot/qwen2.5-coder:0.5b|related_2000_end|5|1/5|20|[0, 60]|0|5|2206/219.6|0.7876/0.6469|0.6469|
|M3R2_pilot/qwen2.5-coder:1.5b|irrelevant_1000_beginning|5|2/5|40|[0, 80]|0|5|1206/115.4|0.6517/0.5343|0.2671|
|M3R2_pilot/qwen2.5-coder:1.5b|irrelevant_1000_end|5|3/5|60|[20, 100]|0|5|1206/206.8|0.8645/0.7062|0.2354|
|M3R2_pilot/qwen2.5-coder:1.5b|irrelevant_2000_beginning|5|3/5|60|[20, 100]|0|5|2206/118.8|1.036/0.8482|0.2827|
|M3R2_pilot/qwen2.5-coder:1.5b|irrelevant_2000_end|5|3/5|60|[20, 100]|0|5|2206/206.8|1.241/1.012|0.3374|
|M3R2_pilot/qwen2.5-coder:1.5b|isolated|5|2/5|40|[0, 80]|0|5|205.4/72.6|0.2228/0.1839|0.09195|
|M3R2_pilot/qwen2.5-coder:1.5b|near_duplicate_1000_beginning|5|2/5|40|[0, 80]|0|5|1206/192.4|0.8428/0.691|0.3455|
|M3R2_pilot/qwen2.5-coder:1.5b|near_duplicate_1000_end|5|5/5|100|[100, 100]|0|5|1206/206.4|0.8735/0.7175|0.1435|
|M3R2_pilot/qwen2.5-coder:1.5b|near_duplicate_2000_beginning|5|2/5|40|[0, 80]|0|5|2206/155.6|1.174/0.9759|0.488|
|M3R2_pilot/qwen2.5-coder:1.5b|near_duplicate_2000_end|5|4/5|80|[40, 100]|0|5|2206/208|1.253/1.017|0.2543|
|M3R2_pilot/qwen2.5-coder:1.5b|related_1000_beginning|5|4/5|80|[40, 100]|0|5|1206/194|0.8378/0.6875|0.1719|
|M3R2_pilot/qwen2.5-coder:1.5b|related_1000_end|5|3/5|60|[20, 100]|0|5|1206/192.4|0.8527/0.7018|0.2339|
|M3R2_pilot/qwen2.5-coder:1.5b|related_2000_beginning|5|1/5|20|[0, 60]|0|5|2206/186.2|1.214/0.9957|0.9957|
|M3R2_pilot/qwen2.5-coder:1.5b|related_2000_end|5|3/5|60|[20, 100]|0|5|2206/193.6|1.215/0.9899|0.33|
|M3_initial/qwen2.5-coder:0.5b|irrelevant/1000|20|15/20|75|[55, 90]|0|20|1000/172.1|1.299/0.9692|0.06461|
|M3_initial/qwen2.5-coder:0.5b|irrelevant/4000|20|13/20|65|[45, 85]|0|20|4000/163.9|3.97/2.778|0.2137|
|M3_initial/qwen2.5-coder:0.5b|near_duplicate/1000|20|9/20|45|[25, 65]|0|20|1000/159.1|1.214/0.8854|0.09838|
|M3_initial/qwen2.5-coder:0.5b|near_duplicate/4000|20|8/20|40|[20, 60]|0|20|4000/151.7|4.015/2.905|0.3631|
|M3_initial/qwen2.5-coder:0.5b|other_tasks/1000|20|9/20|45|[25, 65]|1|20|1000/269.9|1.752/1.368|0.152|
|M3_initial/qwen2.5-coder:0.5b|other_tasks/4000|20|9/20|45|[25, 65]|0|20|4000/159.8|4.21/3.153|0.3504|
|M3_initial/qwen2.5-coder:1.5b|irrelevant/1000|20|19/20|95|[85, 100]|0|20|1000/157.2|2.325/1.823|0.09596|
|M3_initial/qwen2.5-coder:1.5b|irrelevant/4000|20|18/20|90|[75, 100]|0|20|4000/132.1|5.671/3.801|0.2112|
|M3_initial/qwen2.5-coder:1.5b|near_duplicate/1000|20|18/20|90|[75, 100]|0|20|1000/145.9|2.081/1.552|0.08624|
|M3_initial/qwen2.5-coder:1.5b|near_duplicate/4000|20|18/20|90|[75, 100]|0|20|4000/139.8|5.84/4.038|0.2243|
|M3_initial/qwen2.5-coder:1.5b|other_tasks/1000|20|12/20|60|[40, 80]|0|20|1000/177.2|2.356/1.802|0.1502|
|M3_initial/qwen2.5-coder:1.5b|other_tasks/4000|20|15/20|75|[55, 95]|0|20|4000/178.8|6.43/4.675|0.3117|
|M3_isolated/qwen2.5-coder:0.5b|isolated_no_filler|20|12/20|60|[40, 80]|0|20|160.4/161.3|0.7163/0.6005|0.05004|
|M3_isolated/qwen2.5-coder:1.5b|isolated_no_filler|20|18/20|90|[75, 100]|0|20|171.8/98.15|1.046/0.8794|0.04886|
|R1/qwen2.5-coder:0.5b|full_history|40|14/40|35|[20, 50]|5|40|1328/448.4|6.002/4.555|0.3254|
|R1/qwen2.5-coder:0.5b|lossless_compaction|40|16/40|40|[25, 55]|0|40|177/193.7|1.633/1.269|0.07929|
|R1/qwen2.5-coder:0.5b|no_history|40|19/40|47.5|[32.5, 62.5]|0|40|170.6/501.2|3.823/2.993|0.1575|
|R1/qwen2.5-coder:0.5b|oracle_selective|40|17/40|42.5|[27.5, 57.5]|0|40|183.6/196|1.669/1.299|0.07639|
|R1/qwen2.5-coder:0.5b|verbatim_replay|40|15/40|37.5|[22.5, 52.5]|0|40|1468/225.2|4.398/3.404|0.2269|
|R1/qwen2.5-coder:1.5b|full_history|40|22/40|55|[40, 70]|0|40|1328/69.12|4.414/3.392|0.1542|
|R1/qwen2.5-coder:1.5b|lossless_compaction|40|22/40|55|[40, 70]|0|40|177/64.6|1.484/1.166|0.053|
|R1/qwen2.5-coder:1.5b|no_history|40|28/40|70|[55, 85]|0|40|170.6/301.6|5.68/4.514|0.1612|
|R1/qwen2.5-coder:1.5b|oracle_selective|40|23/40|57.5|[42.5, 72.5]|0|40|183.6/63.62|1.467/1.155|0.0502|
|R1/qwen2.5-coder:1.5b|verbatim_replay|40|23/40|57.5|[42.5, 72.5]|0|40|1468/75.22|4.875/3.761|0.1635|
|R1_pilot/qwen2.5-coder:0.5b|full_history|5|4/5|80|[40, 100]|0|5|1223/171.8|0.4412/0.3449|0.08622|
|R1_pilot/qwen2.5-coder:0.5b|lossless_compaction|5|4/5|80|[40, 100]|0|5|150.4/93.8|0.1041/0.08128|0.02032|
|R1_pilot/qwen2.5-coder:0.5b|no_history|5|4/5|80|[40, 100]|0|5|138.4/337.2|0.342/0.2741|0.06852|
|R1_pilot/qwen2.5-coder:0.5b|oracle_selective|5|4/5|80|[40, 100]|0|5|151.4/94.6|0.1065/0.0827|0.02067|
|R1_pilot/qwen2.5-coder:0.5b|verbatim_replay|5|3/5|60|[20, 100]|0|5|1331/141.8|0.4156/0.3158|0.1053|
|R1_pilot/qwen2.5-coder:1.5b|full_history|5|4/5|80|[40, 100]|0|5|1223/36.6|0.4352/0.3351|0.08377|
|R1_pilot/qwen2.5-coder:1.5b|lossless_compaction|5|4/5|80|[40, 100]|0|5|150.4/38.4|0.1165/0.08956|0.02239|
|R1_pilot/qwen2.5-coder:1.5b|no_history|5|5/5|100|[100, 100]|0|5|138.4/239|0.5375/0.4188|0.08377|
|R1_pilot/qwen2.5-coder:1.5b|oracle_selective|5|4/5|80|[40, 100]|0|5|151.4/38.4|0.1136/0.08719|0.0218|
|R1_pilot/qwen2.5-coder:1.5b|verbatim_replay|5|4/5|80|[40, 100]|0|5|1331/41|0.4749/0.3648|0.09121|
|harness_pilot/qwen2.5-coder:0.5b|4000_input_tokens|1|None/0|NA|unavailable|0|1|4000/1|0.209/0.1177|NA|
|harness_pilot/qwen2.5-coder:0.5b|P1|5|None/0|NA|unavailable|0|5|115.4/153|0.1944/0.1147|NA|
|harness_pilot/qwen2.5-coder:0.5b|P3_1|5|None/0|NA|unavailable|0|5|161.4/146.6|0.1979/0.1142|NA|
|harness_pilot/qwen2.5-coder:1.5b|4000_input_tokens|1|None/0|NA|unavailable|0|1|4000/2|0.3355/0.2007|NA|
|harness_pilot/qwen2.5-coder:1.5b|P1|5|None/0|NA|unavailable|0|5|115.4/62|0.2125/0.1292|NA|
|harness_pilot/qwen2.5-coder:1.5b|P3_1|5|None/0|NA|unavailable|0|5|161.4/85.2|0.2713/0.1632|NA|
