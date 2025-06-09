function generateProtocol(child, pastSessions) {

    //var condition_list = ["cond-1A", "cond-1B", "cond-2A", "cond-2B", "cond-1A-locationflip", "cond-1B-locationflip", "cond-2A-locationflip", "cond-2B-locationflip"];
    //select a default condition for the session

    const inputPilotJSON = [
  {
    "audio": "ACORN",
    "images": [
      {
        "id": "acorn-coconut-left",
        "src": "coconut.jpg",
        "position": "left"
      },
      {
        "id": "acorn-coconut-right",
        "src": "acorn.jpg",
        "position": "right"
      }
    ],
    "id": "hard-acorn-coconut"
  },
  {
    "audio": "ACORN",
    "images": [
      {
        "id": "acorn-key-left",
        "src": "key.jpg",
        "position": "left"
      },
      {
        "id": "acorn-key-right",
        "src": "acorn.jpg",
        "position": "right"
      }
    ],
    "id": "easy-acorn-key"
  },
  {
    "audio": "BULLDOZER",
    "images": [
      {
        "id": "bulldozer-orange-left",
        "src": "bulldozer.jpg",
        "position": "left"
      },
      {
        "id": "bulldozer-orange-right",
        "src": "orange.jpg",
        "position": "right"
      }
    ],
    "id": "easy-bulldozer-orange"
  },
  {
    "audio": "BULLDOZER",
    "images": [
      {
        "id": "bulldozer-tractor-left",
        "src": "tractor.jpg",
        "position": "left"
      },
      {
        "id": "bulldozer-tractor-right",
        "src": "bulldozer.jpg",
        "position": "right"
      }
    ],
    "id": "hard-bulldozer-tractor"
  },
  {
    "audio": "CHEESE",
    "images": [
      {
        "id": "cheese-butter-left",
        "src": "cheese.jpg",
        "position": "left"
      },
      {
        "id": "cheese-butter-right",
        "src": "butter.jpg",
        "position": "right"
      }
    ],
    "id": "hard-cheese-butter"
  },
  {
    "audio": "CHEESE",
    "images": [
      {
        "id": "cheese-mud-left",
        "src": "mud.jpg",
        "position": "left"
      },
      {
        "id": "cheese-mud-right",
        "src": "cheese.jpg",
        "position": "right"
      }
    ],
    "id": "easy-cheese-mud"
  },
  {
    "audio": "POTATO",
    "images": [
      {
        "id": "potato-glasses-left",
        "src": "glasses.jpg",
        "position": "left"
      },
      {
        "id": "potato-glasses-right",
        "src": "potato.jpg",
        "position": "right"
      }
    ],
    "id": "easy-potato-glasses"
  },
  {
    "audio": "POTATO",
    "images": [
      {
        "id": "potato-pot-left",
        "src": "pot.jpg",
        "position": "left"
      },
      {
        "id": "potato-pot-right",
        "src": "potato.jpg",
        "position": "right"
      }
    ],
    "id": "hard-potato-pot"
  },
  {
    "audio": "SNAIL",
    "images": [
      {
        "id": "snail-cow-left",
        "src": "snail.jpg",
        "position": "left"
      },
      {
        "id": "snail-cow-right",
        "src": "cow.jpg",
        "position": "right"
      }
    ],
    "id": "easy-snail-cow"
  },
  {
    "audio": "SNAIL",
    "images": [
      {
        "id": "snail-worm-left",
        "src": "snail.jpg",
        "position": "left"
      },
      {
        "id": "snail-worm-right",
        "src": "worm.jpg",
        "position": "right"
      }
    ],
    "id": "hard-snail-worm"
  },
  {
    "audio": "SQUIRREL",
    "images": [
      {
        "id": "squirrel-eagle-left",
        "src": "eagle.jpg",
        "position": "left"
      },
      {
        "id": "squirrel-eagle-right",
        "src": "squirrel.jpg",
        "position": "right"
      }
    ],
    "id": "easy-squirrel-eagle"
  },
  {
    "audio": "SQUIRREL",
    "images": [
      {
        "id": "squirrel-monkey-left",
        "src": "monkey.jpg",
        "position": "left"
      },
      {
        "id": "squirrel-monkey-right",
        "src": "squirrel.jpg",
        "position": "right"
      }
    ],
    "id": "hard-squirrel-monkey"
  },
  {
    "audio": "TURKEY",
    "images": [
      {
        "id": "turkey-goat-left",
        "src": "goat.jpg",
        "position": "left"
      },
      {
        "id": "turkey-goat-right",
        "src": "turkey.jpg",
        "position": "right"
      }
    ],
    "id": "hard-turkey-goat"
  },
  {
    "audio": "TURKEY",
    "images": [
      {
        "id": "turkey-swan-left",
        "src": "swan.jpg",
        "position": "left"
      },
      {
        "id": "turkey-swan-right",
        "src": "turkey.jpg",
        "position": "right"
      }
    ],
    "id": "easy-turkey-swan"
  },
  {
    "audio": "TURTLE",
    "images": [
      {
        "id": "turtle-frog-left",
        "src": "turtle.jpg",
        "position": "left"
      },
      {
        "id": "turtle-frog-right",
        "src": "frog.jpg",
        "position": "right"
      }
    ],
    "id": "hard-turtle-frog"
  },
  {
    "audio": "TURTLE",
    "images": [
      {
        "id": "turtle-horse-left",
        "src": "horse.jpg",
        "position": "left"
      },
      {
        "id": "turtle-horse-right",
        "src": "turtle.jpg",
        "position": "right"
      }
    ],
    "id": "easy-turtle-horse"
  },
  {
    "audio": "COCONUT",
    "images": [
      {
        "id": "acorn-coconut-left",
        "src": "coconut.jpg",
        "position": "left"
      },
      {
        "id": "acorn-coconut-right",
        "src": "acorn.jpg",
        "position": "right"
      }
    ],
    "id": "hard-acorn-coconut-distractor"
  },
  {
    "audio": "KEY",
    "images": [
      {
        "id": "acorn-key-left",
        "src": "key.jpg",
        "position": "left"
      },
      {
        "id": "acorn-key-right",
        "src": "acorn.jpg",
        "position": "right"
      }
    ],
    "id": "easy-acorn-key-distractor"
  },
  {
    "audio": "ORANGE",
    "images": [
      {
        "id": "bulldozer-orange-left",
        "src": "bulldozer.jpg",
        "position": "left"
      },
      {
        "id": "bulldozer-orange-right",
        "src": "orange.jpg",
        "position": "right"
      }
    ],
    "id": "easy-bulldozer-orange-distractor"
  },
  {
    "audio": "TRACTOR",
    "images": [
      {
        "id": "bulldozer-tractor-left",
        "src": "tractor.jpg",
        "position": "left"
      },
      {
        "id": "bulldozer-tractor-right",
        "src": "bulldozer.jpg",
        "position": "right"
      }
    ],
    "id": "hard-bulldozer-tractor-distractor"
  },
  {
    "audio": "BUTTER",
    "images": [
      {
        "id": "cheese-butter-left",
        "src": "cheese.jpg",
        "position": "left"
      },
      {
        "id": "cheese-butter-right",
        "src": "butter.jpg",
        "position": "right"
      }
    ],
    "id": "hard-cheese-butter-distractor"
  },
  {
    "audio": "MUD",
    "images": [
      {
        "id": "cheese-mud-left",
        "src": "mud.jpg",
        "position": "left"
      },
      {
        "id": "cheese-mud-right",
        "src": "cheese.jpg",
        "position": "right"
      }
    ],
    "id": "easy-cheese-mud-distractor"
  },
  {
    "audio": "GLASSES",
    "images": [
      {
        "id": "potato-glasses-left",
        "src": "glasses.jpg",
        "position": "left"
      },
      {
        "id": "potato-glasses-right",
        "src": "potato.jpg",
        "position": "right"
      }
    ],
    "id": "easy-potato-glasses-distractor"
  },
  {
    "audio": "POT",
    "images": [
      {
        "id": "potato-pot-left",
        "src": "pot.jpg",
        "position": "left"
      },
      {
        "id": "potato-pot-right",
        "src": "potato.jpg",
        "position": "right"
      }
    ],
    "id": "hard-potato-pot-distractor"
  },
  {
    "audio": "COW",
    "images": [
      {
        "id": "snail-cow-left",
        "src": "snail.jpg",
        "position": "left"
      },
      {
        "id": "snail-cow-right",
        "src": "cow.jpg",
        "position": "right"
      }
    ],
    "id": "easy-snail-cow-distractor"
  },
  {
    "audio": "WORM",
    "images": [
      {
        "id": "snail-worm-left",
        "src": "snail.jpg",
        "position": "left"
      },
      {
        "id": "snail-worm-right",
        "src": "worm.jpg",
        "position": "right"
      }
    ],
    "id": "hard-snail-worm-distractor"
  },
  {
    "audio": "EAGLE",
    "images": [
      {
        "id": "squirrel-eagle-left",
        "src": "eagle.jpg",
        "position": "left"
      },
      {
        "id": "squirrel-eagle-right",
        "src": "squirrel.jpg",
        "position": "right"
      }
    ],
    "id": "easy-squirrel-eagle-distractor"
  },
  {
    "audio": "MONKEY",
    "images": [
      {
        "id": "squirrel-monkey-left",
        "src": "monkey.jpg",
        "position": "left"
      },
      {
        "id": "squirrel-monkey-right",
        "src": "squirrel.jpg",
        "position": "right"
      }
    ],
    "id": "hard-squirrel-monkey-distractor"
  },
  {
    "audio": "GOAT",
    "images": [
      {
        "id": "turkey-goat-left",
        "src": "goat.jpg",
        "position": "left"
      },
      {
        "id": "turkey-goat-right",
        "src": "turkey.jpg",
        "position": "right"
      }
    ],
    "id": "hard-turkey-goat-distractor"
  },
  {
    "audio": "SWAN",
    "images": [
      {
        "id": "turkey-swan-left",
        "src": "swan.jpg",
        "position": "left"
      },
      {
        "id": "turkey-swan-right",
        "src": "turkey.jpg",
        "position": "right"
      }
    ],
    "id": "easy-turkey-swan-distractor"
  },
  {
    "audio": "FROG",
    "images": [
      {
        "id": "turtle-frog-left",
        "src": "turtle.jpg",
        "position": "left"
      },
      {
        "id": "turtle-frog-right",
        "src": "frog.jpg",
        "position": "right"
      }
    ],
    "id": "hard-turtle-frog-distractor"
  },
  {
    "audio": "HORSE",
    "images": [
      {
        "id": "turtle-horse-left",
        "src": "horse.jpg",
        "position": "left"
      },
      {
        "id": "turtle-horse-right",
        "src": "turtle.jpg",
        "position": "right"
      }
    ],
    "id": "easy-turtle-horse-distractor"
  }
]
    
    const inputAttentionGetters = [
        {
            "id": "attention-getter-balloons",
            "kind": "exp-lookit-video",
             "video": {
                "top": 20,
                "left": 25,
                "loop": false,
                 "width": 50,
                "source": "Balloons"
            }
        },
        {
            "id": "attention-getter-bouncyballs",
             "kind": "exp-lookit-video",
             "video": {
                "top": 20,
                "left": 25,
                "loop": false,
                 "width": 50,
                "source": "BouncyBalls"
            }
        },
        {
            "id": "attention-getter-meadow",
             "kind": "exp-lookit-video",
             "video": {
                "top": 20,
                "left": 25,
                "loop": false,
                 "width": 50,
                "source": "Meadow"
            }
        },
        {
            "id": "attention-getter-mountains",
             "kind": "exp-lookit-video",
             "video": {
                "top": 20,
                "left": 25,
                "loop": false,
                 "width": 50,
                "source": "Mountains"
            }
        }
        ]
        /*,
        {
                    "id": "attention-getter-water",
                    "audio": "acrossTheUniverse000",
                    "images": [{
                            "id": "attention-getter-water-left",
                            "src": "water_left.jpg",
                            "position": "left"
                        },
                        {
                            "id": "attention-getter-water-right",
                            "src": "water_right.jpg",
                            "position": "right"
                        }
                    ]
        },
        {
                    "id": "attention-getter-fireworks",
                    "audio": "acrossTheUniverse016",
                    "images": [{
                            "id": "attention-getter-fireworks-left",
                            "src": "fireworks_left.jpg",
                            "position": "left"
                        },
                        {
                            "id": "attention-getter-fireworks-right",
                            "src": "fireworks_right.jpg",
                            "position": "right"
                        }
                    ]
        },
        {
                    "id": "attention-getter-beach",
                    "audio": "yellow001",
                    "images": [{c
                            "id": "attention-getter-beach-left",
                            "src": "beach_left.jpg",
                            "position": "left"
                        },
                        {
                            "id": "attention-getter-beach-right",
                            "src": "beach_right.jpg",
                            "position": "right"
                        }
                    ]
        },
        {
                    "id": "attention-gettter-mountain",
                    "audio": "yellow001",
                    "images": [{
                            "id": "attention-gettter-mountain-left",
                            "src": "mountain_left.jpg",
                            "position": "left"
                        },
                        {
                            "id": "attention-gettter-mountain-right",
                            "src": "mountain_right.jpg",
                            "position": "right"
                        }
                    ]
    }
    ]
    */
    function shuffleArray(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        // Swap elements
        [arr[i], arr[j]] = [arr[j], arr[i]];
        }
    return arr;
    }
    
    // Group an array by their id, shuffle the elements of each group, and shuffle the groups
    function groupAndShuffle(arr, extractedId) {
        // Group elements by their target word
        let groups = arr.reduce((acc, item) => {
            let id = extractedId(item);
            acc[id] = acc[id] || [];
            acc[id].push(item);
            return acc;
        }, {});
         // Filter for groups with exactly 2 items and shuffle
        let shuffledGroups = Object.values(groups)
        .filter(group => group.length === 2)
        .map(arr => {
        if (Math.random() > 0.5) {
            return [arr[1], arr[0]]; // Swap elements
        }
        return arr; // Keep as is
        });
        return shuffledGroups;
    }
    
    // Flattening our groups of 2 of the same target image and within those our groups of 2 of the same image-pair
    function shuffleGroupedItems(groups, extractedId) {
        let shuffledItems = [
        ...shuffleArray(groups.map(group => group[0]).map(imagepairgroup => imagepairgroup[0])),
        ...shuffleArray(groups.map(group => group[1]).map(imagepairgroup => imagepairgroup[0])),
        ...shuffleArray(groups.map(group => group[0]).map(imagepairgroup => imagepairgroup[1])),
        ...shuffleArray(groups.map(group => group[1]).map(imagepairgroup => imagepairgroup[1]))
        ];
        // Making sure elements with the same ID are not next to each other after shuffling
        for (let index = groups.length - 1; index < shuffledItems.length - 1; index+=(groups.length)) {
            if (extractedId(shuffledItems[index]) == extractedId(shuffledItems[index + 1])) {
                // Starting from the second element of a particular subsection
                let swapIndex = index - (groups.length - 2);
                while (extractedId(shuffledItems[swapIndex]) == extractedId(shuffledItems[index + 1])) {
                    swapIndex++;
                }
            let temp = shuffledItems[swapIndex];
            shuffledItems[swapIndex] = shuffledItems[index];
            shuffledItems[index] = temp;
            }
        }
        return shuffledItems;
    }
    
    // Shuffle trials to shuffle with the condition that images with the same target-distractor image-pair and images with the same target image do not appear close to each other
    function shuffleWithCondition(arr) {
         // Shuffle image-pair conditions (target, distractor) to be in different halves of the same experiment 
        let extractedImagePairId = (item) => { 
            let idSplit = item["id"].split('-')
            return idSplit[0] + "" + idSplit[1];
        }
        let imagePairGroups = groupAndShuffle(arr, extractedImagePairId);
        // Shuffle image-pair groups so that easy and hard trials for the same target image do not appear in the same quarter of the experiment
        let extractedTargetImageId = (item) => item[0]["id"].split("-")[1];
        let targetImageGroups = groupAndShuffle(imagePairGroups, extractedTargetImageId);
        // Shuffle all of the items of the nested groups 
        // Using broader target image ID so that target images are not back-to-back after shuffling
        let extractedBroadTargetId = (item) => item["id"].split("-")[1];
        // Important to note that the items in targetImageItems are groups of image-pairs since we initially grouped the groups of image-pairs by target image. 
        let imagePairItems = shuffleGroupedItems(targetImageGroups, extractedBroadTargetId);
        return imagePairItems;
    }

    /* Shuffles the positions of the images of an input trial 50% of the time
    * Each input trial is of the form 
    { audio: string, id: string, images: [{id: string, src: string, position: left|right}, {id: string, src: string, position: left|right}] }
    */
    function shuffleImages(trial) {
      if (Math.random() > 0.5) {
        [trial["images"][0]["src"], trial["images"][1]["src"]] = [trial["images"][1]["src"], trial["images"][0]["src"]]
      }
    }
    
    function insertCarrierFrames(arr, carrierFrames) {
        let currentCarrierFrames;
        for (let i=0; i < arr.length; i++) {
            if (i % 4 === 0) {
                currentCarrierFrames = shuffleArray(carrierFrames)
            }
            arr[i]["audio"] = currentCarrierFrames[i%4] + "_" + arr[i]["audio"].toLowerCase()
        }
    }
    
    let pilotJSON = shuffleWithCondition(inputPilotJSON) //inputPilotJSON
    pilotJSON.forEach(trial => shuffleImages(trial))
    const carrierFrames = ["where", "find", "look_at", "see"]
    insertCarrierFrames(pilotJSON, carrierFrames)
    console.log(pilotJSON)
    
    let currentAttentionGetters = shuffleArray(inputAttentionGetters.concat(inputAttentionGetters))
    function insertAttentionGetters(arr, agArr) {
        for (let index = 0; index < agArr.length; index++) {
            let insertedIndex = (index+1)*4 + index;
            // Do not insert attention getter in the final position of the trial set
            if (insertedIndex >= arr.length - 1) {
                break;
            }
            arr.splice((index+1)*4 + index, 0, agArr[index]);
        }
    }
    
    // Function to randomly select one item from an array
    const getRandomItem = (array) => array[Math.floor(Math.random() * array.length)];

    insertAttentionGetters(pilotJSON, currentAttentionGetters)
    
    pilotJSON = [
        ...pilotJSON,
        {
                    "id": "great-job",
                    "audio": "great_job",
                    "images": [{
                            "id": "calib-duck-great-job",
                            "src": "calib_duck.jpg",
                            "position": "center"
                        }
                    ]
        }]
    
    var debrief_text = "You just completed this study! After you exit this experiment, we will check that your consent video meets our eligibility criteria and send you a $5 Amazon gift card (US) within one week of participating. </br></br>In this study, we are interested in how babies learn that words, such as <i>bulldozer</i>, refer to different types of bulldozers, but not to similar looking categories, like types of tractors. Your baby saw some pictures of objects that are labeled (for example, a bulldozer), paired with objects that differ in how similar they are to the labeled object (for example, a tractor and an orange). We wonder if babies will make more mistakes with the more similar objects compared to the objects that are more different. All babies in this study were shown the same pairs of pictures but the order in which they appeared and the ordering of the pictures were both randomized.</br></br>Babies know more about words than they are able to say, so we look at what babies <i>understand</i> about words by seeing what they look at during the study. There are many reasons why your baby might look to one kind of object over another, and your baby likely looked at pictures differently than another child based on their unique experiences with these categories of words. For example, your baby may not know the word <i>squirrel</i> or maybe your baby eats a lot of oranges at home that look like the ones in our study. If we understand how this process changes and is supposed to change across development, we can provide better assessments and interventions for children who struggle with early category learning, including late talkers and children with ASD.<br/><br/>To learn more, <a href='https://pmc.ncbi.nlm.nih.gov/articles/PMC2630708/'>here</a> is a link to a study about how children with ASD process categories differently and <a href='https://www.nature.com/articles/s41467-023-44529-9'>here</a> is a link to a study led by the principal investigator of our lab, Dr. Bria Long, about how the way children think about categories changes as they get older. You can also <a href='https://www.vislearnlab.org/'>visit our website</a> to learn more about our research!"

    const condition = "pilot"

    let frames = {
        "eligibility-survey": {
            "kind": "exp-lookit-survey",
            "formSchema": {
                "schema": {
                    "type": "object",
                    "title": "Eligibility survey </br></br> <img src='https://ucsdlearninglabs.org/stimuli/img/USA_map.jpg' alt='US map'  class='center'>",
                    "properties": {
                        "liveUS": {
                            "enum": [
                                "yes",
                                "no"
                            ],
                            "type": "string",
                            "title": "Do you (the grown-up) and your baby live in the United States of America (USA)?",
                            "required": true
                        }
                    }
                },
                "options": {
                    "fields": {
                        "liveUS": {
                            "type": "radio",
                            "message": "This question is required to be eligible for the study! Please answer this question.",
                            "validator": "required-field",
                            "sort": false
                        }
                    }
                }
            },
            "nextButtonText": "Continue",
            "showPreviousButton": false
        },
        "eligibility-procedure": {
            "kind": "exp-frame-select",
            "frameOptions": [
                {
                    "kind": "exp-lookit-text",
                    "blocks": [
                        {
                            "emph": true,
                            "text": "Let's start the study!"
                        },
                        {
                            "text": "Press NEXT below to learn about the study and how to get set up to participate!"
                        }
                    ]
                },
                {
                    "kind": "exp-lookit-text",
                    "nextButtonText": " ",
                    "blocks": [{
                            "emph": true,
                            "text": "This study is only open to families in the United States."
                        },
                        {
                            "text": "Thank you so much for your interest in our study! Unfortunately, this study is only open to families in the United States due to difficulties with compensating families in other countries. In the future, we are hoping to change that since we are interested in the language development of babies all over the world!"
                        },
                        {
                            "text": "If you live outside of the United States, <a href='https://lookit.mit.edu/studies/'> please click here to exit and go back to the Lookit Studies page.</a> If you choose to participate in the study and you live outside of the United States, we won't be able to use your data or compensate you for your time. Thank you so much for understanding!"
                        }
                    ]
                }
            ],
            "generateProperties": "function(expData, sequence, child, pastSessions) {var formData = expData['0-eligibility-survey'].formData; if (formData.liveUS == 'yes') { console.log('eligible'); return { 'whichFrames': 0, 'ELIGIBLE': true } } else { console.log('ineligible'); return { 'whichFrames': 1,  'ELIGIBLE': false } } }",
            "commonFrameProperties": {
                "showPreviousButton": false
            }
        },
        "study-intro": {
            "kind": "exp-lookit-instruction-video",
            "baseDir": "https://ucsdlearninglabs.org/stimuli/",
            "instructionsVideo": "instructions1",
            "videoTypes": [
                "mp4"
            ],
            "introText": "Welcome to the study! Please watch this video to get started. \n(Or you can read the summary to the right if you prefer.)",
            "transcriptTitle": "Video summary",
            "transcriptBlocks": [{
                    "title": "Background information about the study",
                    "listblocks": [{
                            "text": "Your baby does not need to be with you at this point in the study. We will let you know when it is time to get your baby."
                        },
                        {
                            "text": "Over the first two years of life, babies learn to link the words they hear with the objects they experience in their environment. Yet, words refer to entire categories of things in the world. In this study, We want to understand whether the words that babies know are limited to the kinds of examples they experience in their life or whether words are linked with both familiar and unfamiliar examples."
                        }
                    ]
                },
                {
                    "title": "Preview of what your baby will see"
                },
                {
                    "listblocks": [{
                        "text": "Your baby will be shown two objects on the screen; one on the left and one on the right. Then your baby will hear one of the objects named. Sometimes the objects shown will be animals or toys your baby may have seen before, and other times the objects will be less familiar. If children only look at incorrect objects when they are very similar to the correct object, that means they understand that words refer to entire categories of things."
                    }]
                },
                {
                    "title": "What's next?",
                    "listblocks": [{
                            "text": "Because this is an online study, we will check to make sure that your webcam is set up and working properly on the next page, so we can record your baby’s looking behavior during the study."
                        },
                        {
                            "text": "Following that page, you will be given an opportunity to review the consent information and we will ask that you record a short video of yourself giving consent to participate in this study."
                        },
                        {
                            "text": "We will then give you detailed information about what to do during the study and how to position yourself and baby before starting the study. In total, you will have to advance through 5 pages before starting the study."
                        }
                    ]
                }
            ],
            "warningText": "Please watch the video or read the summary before proceeding.",
            "nextButtonText": "I'm ready to make sure my webcam is connected!",
            "title": "Study instructions",
            "showPreviousButton": false
        },
        "webcam-display": {
            "kind": "exp-lookit-webcam-display",
            "blocks": [
                {
                    "title": "Let's check your webcam one last time!",
                    "listblocks": [
                        {
                            "text": "Check that you can see that only your child is easily visible"
                        },
                        {
                            "text": "Press the next button to begin the study"
                        }
                    ]
                }
            ],
            "nextButtonText": "Start the study!",
            "showPreviousButton": true,
            "displayFullscreenOverride": true,
            "startRecordingAutomatically": false
        },
        "exp-get-ready": {
            "kind": "exp-lookit-images-audio",
            "baseDir": "https://ucsdlearninglabs.org/stimuli/",
            "audio": "get_ready",
            "images": [{
                "id": "begin",
                "src": "calib_duck.jpg",
                "top": 30,
                "left": 40,
                "width": 20
            }],
            "autoProceed": true,
            "doRecording": false,
            "audioTypes": [
                "mp3",
                "ogg"
            ],
            "backgroundColor": "gray",
            "pageColor": "gray",
            "parentTextBlock": {
                "text": "Please close your eyes!",
                "title": "Get ready!"
            }

        },
        "video-config": {
            "kind": "exp-video-config",
            "troubleshootingIntro": "If you’re having any difficulties getting your webcam set up, please feel free to email the Visual Learning Learning Lab at vislearnlab@ucsd.edu."
        },
        "exp-calibration": {
            "kind": "exp-lookit-calibration",
            "baseDir": "https://ucsdlearninglabs.org/stimuli/",
            "audioTypes": [
                "ogg",
                "mp3"
            ],
            "calibrationImage": "calib_duck.jpg",
            "calibrationLength": 3000,
            "calibrationPositions": [
                "center",
                "left",
                "right"
            ],
            "calibrationAudio": [{
                "src": "https://ucsdlearninglabs.org/stimuli/mp3/pinwheel.mp3",
                "type": "audio/mp3"
            }],
            "calibrationImageAnimation": "bounce",
            "doRecording": true,
            "backgroundColor": "gray",
            "showWaitForRecordingMessage": true,
            "showWaitForUploadingMessage": true,
            "waitForRecordingMessage": " ",
            "waitForUploadMessage": " ",
            "waitForRecordingMessageColor": "gray",
            "waitForUploadMessageColor": "gray"
        },
        "pilot": {
            "kind": "group",
            "frameList": pilotJSON,
            "commonFrameProperties": {
                "kind": "exp-lookit-images-audio",
                "baseDir": "https://ucsdlearninglabs.org/stimuli/",
                "pageColor": "gray",
                "maximizesDisplay": true,
                "durationSeconds": 7.2,
                "audioTypes": [
                    "mp3", "ogg"
                ],
                "videoTypes": [
                    "mp4"
                ],
                "autoProceed": true,
                "backgroundColor": "gray",
                "announcementLength": 0,
                "pauseWhenExitingFullscreen": true,
                "allowUserPause": true,
                "frameOffsetAfterPause": 1,
                "pausedText": "The study is paused. \n\n Please reposition your baby and press the space bar to continue. \n\n If you would like to end the study press ctrl-X or F1.",
                "doRecording": true,
                "showWaitForRecordingMessage": true,
                "showWaitForUploadingMessage": true,
                "waitForRecordingMessage": " ",
                "waitForUploadMessage": " ",
                "waitForRecordingMessageColor": "gray",
                "waitForUploadMessageColor": "gray"
            }
        },
        "video-consent": {
            "kind": "exp-lookit-video-consent",
            "template": "consent_005",
            "PIName": "Bria Long",
            "PIContact": "Visual Learning Lab at vislearnlab@ucsd.edu",
            "institution": "University of California, San Diego",
            "purpose": "We are running this study to better understand how children develop their language and category representations. This research study aims to to understand how differences in children’s language learning are related to how they learn categories from their everyday visual experiences. We will investigate how they represent and interpret different categories and objects across age and interact with different types and forms of objects.",
            "procedures": "During the study, your child will play different games and activities. The activities will examine your child's linguistic, categorization, or cognitive skills. In one game, your child may play a picture matching game where your child matches a word heard with one of up to 4 images on a screen. In other games, for example, your child may play a ball-identifying game where they identify the box a ball is placed in after the boxes are moved around, or an object-labeling game where your child sees an object or a drawing on the screen and then matches them with one of up to 4 new objects on the screen. All objects and words used in this study will be age-appropriate. Children will identify their choices in these games either by looking at it, pointing at it, or indicating their choice to a parent who then performs one of the actions. The alternative to being in this study is not to participate.",
            "voluntary_participation": "Refusal to participate will involve no penalty or loss of compensation. Further, if you decide to stop participating, you can email us and we can remove any information collected about you and your child if you would like us to. You can also email us at any point after the study to withdraw permission and any information collected about you and your child will be deleted and not used for future research. Any deletion of information will not be held against you.",
            "risk_statement": "There are minimal risks involved with this study. The main risk is a loss of confidentiality. The other associated risks are mild boredom or anxiety about task performance. Should the child participant experience mild boredom or anxiety, we do not believe this will leave a lasting impact.",
            "payment": "We cannot promise any benefit to you or to others from you participating in this research. However, possible benefits may include enjoyment from engaging in the study because of the stimulating nature of the experimental games. Parents may also benefit from the satisfaction of having contributed to research on development in early childhood. There are also potential benefits to educational and public policy regarding the benefits of supporting language development in diverse populations and in children who struggle with early category learning.",
            "datause": "Study information stored by researchers will be labeled with a subject code instead of your name or other information that can easily identify you, which will be kept separate from the rest of the study information. While we cannot guarantee complete confidentiality, we will limit access to information, documents, or recordings of you and your child. Only people who have a need to review your information, documents, or recordings will have access. These people might include:<br><ul><li>Members of the research team and other staff or representatives of UCSD whose work is related to the research or to protecting your rights and safety.</li><li>Representatives of the study sponsor or product manufacturer</li><li>Representatives of Federal and other regulatory agencies who make sure the study is done properly and that your rights and safety are protected.</li></ul>According to the Lookit Terms of Use, we may download local copies of your Lookit data, including study data and video, and account, child, and demographic survey data from participants who have participated in their studies. Lookit may also keep copies of this data, including study data and video, indefinitely. Our research team also retains ownership of study data, including video, for our own studies. You cannot take part in this study without agreeing to the Lookit Terms of Use.",
            "additional_video_privacy_statement": "These video recordings will include your and your child’s faces and/or parts of your or your child’s bodies. While these videos will be subject to the confidentiality conditions described in this form, it is possible that someone who knows you well may be able to identify you from the photos and know you are participating in this study. To minimize this possibility, your videos will only be shared within the research team and people who have a need to review your recordings listed above. It will not be used in publications or for external research unless you explicitly provide permission to do so. Further, if you would not like us to use your recordings at any point in the future, you can email us to withdraw permission and all recordings of your child and you will be deleted and not used for future research.",
            "gdpr": false,
            "research_rights_statement": "If before or during your participation in the study you have questions about your rights as a research participant, or you want to talk to someone outside the research team, please contact UC San Diego Office of IRB Administration at 858-246-4777 or irb@ucsd.edu",
            "additional_segments": [
            {
                "title": "Will I be compensated for participating in the research?",
                "text": "You will receive $5 for completing this study for your time and effort as is standard on Children Helping Science. You will only receive compensation once per child and provided your child is visible at some point and in the age range specified by the study. Compensation will take the form of an Amazon gift card, typically sent to you electronically within a week. Compensation does not depend on finishing the whole study and you can withdraw from the study at any point without affecting your compensation."
            }
            ]
        },
        "study-instructions": {
            "kind": "exp-lookit-instruction-video",
            "baseDir": "https://ucsdlearninglabs.org/stimuli/",
            "instructionsVideo": "instructions2",
            "videoTypes": [
                "mp4"
            ],
            "introText": "Let's get ready! Please watch this video to learn what to do during the study. \n(Or you can read the summary to the right if you prefer.)",
            "transcriptTitle": "Video summary",
            "transcriptBlocks": [{
                    "title": "What to do during the study:",
                    "listblocks": [{
                            "text": "If your child gets fussy or distracted during the study, or you need to attend to something else for a moment, you can pause the study by pressing the spacebar."
                        },
                        {
                            "text": "If you notice that your baby is becoming bored or too fussy to finish the study, that is perfectly OK and quite common. You can stop at any point."
                        },
                        {
                            "text": "If you need to end the study early, you can press ctrl-X or the F1 key to end the study. Select <b>“exit”</b> in the box that will appear on the screen. This will take you to the end of the study."
                        },
                        {
                            "text": "Even if you end the study early we can still use the data from the parts that your baby was looking — you don’t need to finish the study for your data to be usable."
                        }
                    ]
                },
                {
                    "title": "Your role during the study:"
                },
                {
                    "listblocks": [{
                            "text": "Your job is to keep your baby seated on your lap and facing the computer screen so we will be able to see their eyes during the whole study and so that we will not be able to see any of your face or anyone else’s face. On the next page you will see an example of what this should look like."
                        },
                        {
                            "text": "Don’t worry if you feel your baby becoming bored. Even if your baby only looks at the screen a little bit, we are still collecting valuable data from your baby."
                        }
                    ]
                },
                {
                    "title": "Please close your eyes during the study"
                },
                {
                    "listblocks": [{
                            "text": "The most important role you have during the study is to keep your eyes closed. We know this sounds a little strange, but believe it or not, your baby is learning from you and where you look at every moment. "
                        },
                        {
                            "text": "We also ask that you don’t talk to your baby or try to direct their attention in any way during the study. We also ask that you move the cursor out of frame before the study begins so as to not direct their attention towards it."
                        },
                        {
                            "text": "You will hear an audio prompt when the study is finished letting you know that the study is over and that you can open your eyes. The study will last about 5 minutes in total."
                        }
                    ]
                },
                {
                    "title": "What to do when the study is finished:",
                    "listblocks": [{
                            "text": "Once the study has finished playing, you’ll be given an opportunity to report any technical problems you may have experienced along the way."
                        },
                        {
                            "text": "Lastly, you’ll be able to select a privacy level for your videos."
                        }
                    ]
                }
            ],
            "warningText": "Please watch the video or read the summary before proceeding.",
            "nextButtonText": "Getting in position",
            "title": "Study instructions",
            "showPreviousButton": false
        },
        "setup-instructions": {
            "kind": "exp-lookit-instructions",
            "blocks": [{
                    "title": "Caregiver's role",
                    "listblocks": [{
                            "text": "Keep your baby facing forward and seated on your lap."
                        },
                        {
                            "text": "Close your eyes, and try your best to avoid talking or pointing to your baby."
                        }
                    ]
                },
                {
                    "text": "Because this is an online study, we will check to make sure your webcam is working so that we can only see your baby during the study. Please sit facing the monitor, holding your child on your lap, like you see below. Your child can sit or stand as long as <strong> the webcam is angled up or down so that your child's eyes are visible and your eyes are not</strong>. If you're not sure if only your child's eyes will be visible, you can check the video preview on the right side of the screen!",
                    "image": {
                        "alt": "Example image showing a mom holding her child on lap.",
                        "src": "https://ucsdlearninglabs.org/stimuli/img/placeholder_lap_image.jpg"
                    },
                    "title": "Holding your baby"
                },
                {
                    "text": "This study requires that your child listens to some sentences labeling objects. Please listen to the sample audio on this page and adjust your volume level so that it resembles a person's voice in the room.",
                    "title": "Sound check",
                    "mediaBlock": {
                        "text": "You should hear 'Ready to go?'",
                        "isVideo": false,
                        "sources": [{
                                "src": "https://ucsdlearninglabs.org/stimuli/mp3/ready_to_go.mp3",
                                "type": "audio/mp3"
                            },
                            {
                                "src": "https://ucsdlearninglabs.org/stimuli/mp3/ready_to_go.mp3",
                                "type": "audio/ogg"
                            }
                        ],
                        "mustPlay": true,
                        "warningText": "Please try playing the sample audio."
                    }
                }
            ],
            "showWebcam": true,
            "requireTestVideo": true,
            "showRecordMenu": true,
            "webcamBlocks": [{
                "title": "This is what your video will look like",
                "listblocks": [{
                        "text": "If possible, you should position yourself and your baby so that they are seated on your lap with the computer on another surface (i.e., table) in a room that is <b>well lit </b> and has few distrations."
                    },
                    {
                        "text": "You should check to make sure we will be able to see your child's face well and not see your face."
                    }
                ]
            }],
            "nextButtonText": "Next"
        },
        "parent-exit-survey": {
            "kind": "exp-lookit-exit-survey",
            "debriefing": {
                "text": debrief_text,
                "image": {
                    "alt": "thank you",
                    "src": "https://ucsdlearninglabs.org/stimuli/img/exit_survey_image.jpg"
                },
                "title": "Thank you!"
            }
        }
    };
    
    let frame_sequence = [
        "eligibility-survey",
        "eligibility-procedure",
        "study-intro",
        "video-config",
        "video-consent",
        "study-instructions",
        "setup-instructions",
        "webcam-display",
        "exp-get-ready",
        "exp-calibration",
        condition,
        "parent-exit-survey"
    ]
    console.log(frames)
    console.log(frame_sequence)
    return {
        frames: frames,
        sequence: frame_sequence
    };
}