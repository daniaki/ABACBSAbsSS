// Forward declare jQuery"s `$` symbol
"use strict";
jQuery, $;


function plotDemographics(abstracts) {
  let data = {'abstracts': []};
  if (abstracts !== undefined) {
    data.abstracts = abstracts;
  }
  console.log(data);
  $.ajax({
    url: window.location.pathname,
    type: 'GET',
    data: data,
    success: function (data) {
      // Create pie chart for `gender`, `stage` and 'aot'
      let keyList = ['gender', 'stage', 'aot'];
      for(let i=0; i < keyList.length; i++) {
        let type = keyList[i];
        console.log(type);
        console.log(data);
        let plotData = [{values: [], labels: [], type: 'pie'}];
        for (let key in data[type]) {
          if (data[type].hasOwnProperty(key)) {
            plotData[0].values.push(parseInt(data[type][key]));
            plotData[0].labels.push(key);
          } else {
            console.log("'data." + type +  " is missing own property " + key);
            console.log(data);
          }
        }

        let title = null;
        let id = null;
        if (type === 'gender') {
          id = 'gender-plot';
          title = 'Gender';
        }
        else if (type === 'aot') {
          id = 'aot-plot';
          title = 'Aboriginal or Torres Straight Islander'
        }
        else if (type === 'stage') {
          id = 'stage-plot';
          title = 'Career Stage';
        }
        else {
          console.log("Unknown type: " + type);
        }

        let layout = {
          title: title,
          yaxis: {
            automargin: true,
          },
          xaxis: {
            automargin: true,
          }
        };
        // console.log(plotData);
        Plotly.newPlot(id, plotData, layout);
      }

      // State plot
      let plotData = [{x: [], y: [], type: 'bar'}];
      let type = 'state';
      for (let key in data[type]) {
        if (data[type].hasOwnProperty(key)) {
          plotData[0].y.push(parseInt(data[type][key]));
          plotData[0].x.push(key);
        } else {
          console.log("'data." + type +  " is missing own property " + key);
          console.log(data);
        }
      }
      let layout = {
        title: 'State',
        yaxis: {
          automargin: true,
        },
        xaxis: {
          automargin: true,
        }
      };
      console.log(plotData);
      Plotly.newPlot('state-plot', plotData, layout);

    },
    error : function(xhr, errmsg, err) {
      console.log(xhr.status + ": " + xhr.responseText);
    }
  });
}


$("document").ready(function() {
  plotDemographics();
  window.onresize = function() {
    Plotly.Plots.resize('stage-plot');
    Plotly.Plots.resize('state-plot');
    Plotly.Plots.resize('gender-plot');
    Plotly.Plots.resize('aot-plot');
  };
});