include <../../../../openscad/libs/NopSCADlib/lib.scad>

m2Hole = 2.4;

boardLength = 70.05;
boardWidth = 50.2;

boardHoleDiameter = m2Hole;
boardHoleWall = 1.1;

boardMinHeight = 17;
boardPCBThickness = 1.5;

usbCWidth = 9.4;
usbCHeight=4;

wallThickness_calc = 2.0;
bottomTopThickness = 2.0;
generalPadding = 4;

paddingBack_calc         = generalPadding;
paddingFront_calc        = generalPadding + 30;
paddingRight_calc        = generalPadding + 4;
paddingLeft_calc         = generalPadding;

containerLength = paddingBack_calc + boardLength + paddingFront_calc;
containerWidth = paddingLeft_calc + paddingRight_calc + boardWidth;

standoffHeight_calc = 15.0;

boardZero = [wallThickness_calc+paddingBack_calc, wallThickness_calc + paddingLeft_calc, standoffHeight_calc+bottomTopThickness];

// pb stands for powerBoard
pbWidth = 17.5;
pbLength = 28.4;

pbBaseThickness = 4;
pbWallThickness = 2;
pbBoardThickness = 1.1;

pbZero = [wallThickness_calc + paddingBack_calc + boardLength + paddingFront_calc/2 - pbWidth/2, wallThickness_calc, bottomTopThickness+pbBaseThickness];
pbRelZero = pbZero - boardZero;

// power button
buttonWidth = 8.6;
buttonDepth = 14.3;
buttonWallThickness = 3;
buttonZero = [wallThickness_calc + paddingBack_calc + boardLength + paddingFront_calc/2 - buttonWidth/2, wallThickness_calc + containerWidth-buttonDepth, bottomTopThickness];

// pms
pmsHoleDiameter = m2Hole;
pmsWidth = 38.2;
pmsLength = 50.25;
pmsHeight = 21.3;
pmsHoleWall = 1.85;
pmsRelZeroX = -2;

// fan
fanWidth = 30;
fanHeight = 7.8;
fanHoleWall = 1.6;
m3Hole = 3.3;
fanHoleOffset = m3Hole/2 + fanHoleWall;

fanZero = [wallThickness_calc + boardLength, containerWidth-wallThickness_calc-fanWidth,0];
fanRelZero = fanZero - boardZero;

// calibrateButton
calButtonRelZero = [56,7.4,6.5];


containerHeight = standoffHeight_calc + boardPCBThickness + boardMinHeight + generalPadding + pmsHeight;

translate(boardZero){
    difference(){
    /*
        cube([boardLength, boardWidth, boardPCBThickness]);
        translate([calButtonRelZero[0],calButtonRelZero[1],boardPCBThickness]){
            #cube([5, 5, calButtonRelZero[2]]);
        }
        #translate([0,0,containerHeight-pmsHeight-boardZero[2]]) cube([pmsLength, pmsWidth, pmsHeight]);
    */
        /*
        translate([boardHoleDiameter/2 + boardHoleWall, boardHoleDiameter/2 + boardHoleWall,0])
            #cylinder(d=boardHoleDiameter, h = 100);

        translate([-boardHoleDiameter/2 - boardHoleWall+boardLength, boardHoleDiameter/2 + boardHoleWall,0])
            #cylinder(d=boardHoleDiameter, h = 100);

        translate([-boardHoleDiameter/2 - boardHoleWall+boardLength, boardHoleDiameter/2 + boardHoleWall,0])
            #cylinder(d=boardHoleDiameter, h = 100);
        */
    }
}

include <../../../../openscad/libs/YAPP_Box/library/YAPPgenerator_v21.scad>


// Note: length/lengte refers to X axis, 
//       width/breedte to Y, 
//       height/hoogte to Z

/*
            padding-back>|<---- pcb length ---->|<padding-front
                                 RIGHT
                   0    X-ax ---> 
               +----------------------------------------+   ---
               |                                        |    ^
               |                                        |   padding-right 
             ^ |                                        |    v
             | |    -5,y +----------------------+       |   ---              
        B    Y |         | 0,y              x,y |       |     ^              F
        A    - |         |                      |       |     |              R
        C    a |         |                      |       |     | pcb width    O
        K    x |         |                      |       |     |              N
               |         | 0,0              x,0 |       |     v              T
               |   -5,0  +----------------------+       |   ---
               |                                        |    padding-left
             0 +----------------------------------------+   ---
               0    X-ax --->
                                 LEFT
*/

// Override the default facet count of 20
facetCount = 15;

//-- which part(s) do you want to print?
printBaseShell        = true;
printLidShell         = true;
printSwitchExtenders  = true;

//-- pcb dimensions -- very important!!!
pcbLength           = boardLength;
pcbWidth            = boardWidth;
pcbThickness        = boardPCBThickness;
                            
//-- padding between pcb and inside wall
paddingFront        = paddingFront_calc;
paddingBack         = paddingBack_calc;
paddingRight        = paddingRight_calc;
paddingLeft         = paddingLeft_calc;

//-- Edit these parameters for your own box dimensions
wallThickness       = wallThickness_calc;
basePlaneThickness  = bottomTopThickness;
lidPlaneThickness   = bottomTopThickness;


//-- ridge where base and lid off box can overlap
//-- Make sure this isn't less than lidWallHeight
ridgeHeight         = 3.0;
ridgeSlack          = 0.2;
roundRadius         = 2.0;

//-- How much the PCB needs to be raised from the base
//-- to leave room for solderings and whatnot
standoffHeight      = standoffHeight_calc;  //-- only used for showPCB
standoffPinDiameter = boardHoleDiameter;
standoffHoleSlack   = 0.4;
standoffDiameter    = 6;

//-- Total height of box = basePlaneThickness + lidPlaneThickness 
//--                     + baseWallHeight + lidWallHeight
//-- space between pcb and lidPlane :=
//--      (bottonWallHeight+lidWallHeight) - (standoffHeight+pcbThickness)
lidWallHeight       = 3;
baseWallHeight      = containerHeight - 3;

//-- D E B U G -----------------//-> Default ---------
showSideBySide      = true;     //-> true
onLidGap            = 0;
shiftLid            = 1;
hideLidWalls        = false;    //-> false
hideBaseWalls       = false;    //-> false
colorLid            = "silver";
colorBase           = "lightgray";
showOrientation     = true;
showPCB             = false;
showSwitches        = false;
showPCBmarkers      = false;
showShellZero       = false;
showCenterMarkers   = false;
inspectX            = 0;        //-> 0=none (>0 from front, <0 from back)
inspectY            = 0;        //-> 0=none (>0 from left, <0 from right)
inspectLightTubes   = 0;        //-> { -1 | 0 | 1 }
inspectButtons      = 0;        //-> { -1 | 0 | 1 }
//-- D E B U G ---------------------------------------


//-- pcb_standoffs  -- origin is pcb[0,0,0]
// (0) = posx
// (1) = posy
// (2) = standoffHeight
// (3) = filletRadius (0 = auto size)
// (n) = { yappBoth | yappLidOnly | yappBaseOnly }
// (n) = { yappHole, YappPin }
// (n) = { yappAllCorners | yappFrontLeft | yappFrontRight | yappBackLeft | yappBackRight }
// (n) = { yappAddFillet }

pcbStands =    [
                   // board
                   [boardHoleWall+standoffPinDiameter/2, boardHoleWall+standoffPinDiameter/2, standoffHeight, 2, yappBaseOnly, yappAllCorners, yappAddFillet], 
               ];

//-- base plane    -- origin is pcb[0,0,0]
// (0) = posx
// (1) = posy
// (2) = width
// (3) = length
// (4) = angle
// (n) = { yappRectangle | yappCircle }
// (n) = { yappCenter }
cutoutsBase =   [
                ];

//-- Lid plane    -- origin is pcb[0,0,0]
// (0) = posx
// (1) = posy
// (2) = width
// (3) = length
// (4) = angle
// (n) = { yappRectangle | yappCircle }
// (n) = { yappCenter }
cutoutsLid  =   [
                    // pmsHoles
                    [pmsHoleWall+pmsRelZeroX+pmsHoleDiameter/2,           pmsHoleWall-paddingLeft_calc+pmsHoleDiameter/2, pmsHoleDiameter, 0,0,yappCircle,yappCenter],
                    [pmsLength-pmsHoleWall+pmsRelZeroX-pmsHoleDiameter/2, pmsHoleWall-paddingLeft_calc+pmsHoleDiameter/2, pmsHoleDiameter, 0,0,yappCircle,yappCenter],
                    [pmsLength-pmsHoleWall+pmsRelZeroX-pmsHoleDiameter/2, pmsWidth-pmsHoleWall-paddingLeft_calc-pmsHoleDiameter/2, pmsHoleDiameter, 0,0,yappCircle,yappCenter],
                    [pmsHoleWall+pmsRelZeroX+pmsHoleDiameter/2,           pmsWidth-pmsHoleWall-paddingLeft_calc-pmsHoleDiameter/2, pmsHoleDiameter, 0,0,yappCircle,yappCenter],

                    // fan screw holes
                    [fanRelZero[0] + fanHoleOffset,            fanRelZero[1] + fanHoleOffset,            m3Hole, 0, 0, yappCircle],
                    [fanRelZero[0] + fanHoleOffset,            fanRelZero[1] + fanWidth - fanHoleOffset, m3Hole, 0, 0, yappCircle],
                    [fanRelZero[0] + fanWidth - fanHoleOffset, fanRelZero[1] + fanWidth - fanHoleOffset, m3Hole, 0, 0, yappCircle],
                    [fanRelZero[0] + fanWidth - fanHoleOffset, fanRelZero[1] + fanHoleOffset,            m3Hole, 0, 0, yappCircle],
                ];

//-- cutoutsGrill    -- origin is pcb[x0,y0,zx]
// (0) = xPos
// (1) = yPos
// (2) = grillWidth
// (3) = grillLength
// (4) = gWidth
// (5) = gSpace
// (6) = gAngle
// (7) = plane {"base" | "lid" }
// (8) = {polygon points}}

cutoutsGrill = [
    [fanRelZero[0]+1.5*fanHoleOffset, fanRelZero[1]+1.5*fanHoleOffset, fanWidth-3*fanHoleOffset, fanWidth-3*fanHoleOffset, 2, 1.4,  45, "lid"]
];


//-- front plane  -- origin is pcb[0,0,0]
// (0) = posy
// (1) = posz
// (2) = width
// (3) = height
// (4) = angle
// (n) = { yappRectangle | yappCircle }
// (n) = { yappCenter }
cutoutsFront =  [
                ];
//-- origin of labels is box [0,0,0]
// (0) = posx
// (1) = posy/z
// (2) = orientation
// (3) = depth
// (4) = plane {lid | base | left | right | front | back }
// (5) = font
// (6) = size
// (7) = "label text"
labelsPlane = [
              ];
//-- back plane  -- origin is pcb[0,0,0]
// (0) = posy
// (1) = posz
// (2) = width
// (3) = height
// (4) = angle
// (n) = { yappRectangle | yappCircle }
// (n) = { yappCenter }
cutoutsBack =   [
                ];

//-- left plane   -- origin is pcb[0,0,0]
// (0) = posx
// (1) = posz
// (2) = width
// (3) = height
// (4) = angle
// (n) = { yappRectangle | yappCircle }
// (n) = { yappCenter }
cutoutsLeft =   [
                    [pmsRelZeroX,-standoffHeight+containerHeight-pmsHeight-1.45,pmsLength,pmsHeight,0,yappRectangle]
                ];

//-- right plane   -- origin is pcb[0,0,0]
// (0) = posx
// (1) = posz
// (2) = width
// (3) = height
// (4) = angle
// (n) = { yappRectangle | yappCircle }
// (n) = { yappCenter }
cutoutsRight =  [
                ];

//-- connectors 
//-- normal         : origen = box[0,0,0]
//-- yappConnWithPCB: origen = pcb[0,0,0]
// (0) = posx
// (1) = posy
// (2) = pcbStandHeight
// (3) = screwDiameter
// (4) = screwHeadDiameter
// (5) = insertDiameter
// (6) = outsideDiameter
// (7) = filletRadius (0 = auto size)
// (n) = { yappConnWithPCB }
// (n) = { yappAllCorners | yappFrontLeft | yappFrondRight | yappBackLeft | yappBackRight }
// (n) = { yappAddFillet }
connectors   = [ 
               ];

//-- base mounts -- origen = box[x0,y0]
// (0) = posx | posy
// (1) = screwDiameter
// (2) = width
// (3) = height
// (n) = yappLeft / yappRight / yappFront / yappBack (one or more)
// (n) = { yappCenter }
// (n) = { yappAddFillet }
baseMounts   =  [
                ];

//-- snap Joins -- origen = box[x0,y0]
// (0) = posx | posy
// (1) = width
// (n) = yappLeft / yappRight / yappFront / yappBack (one or more)
// (n) = { yappSymmetric }
snapJoins   =   [
                  [(1*containerLength/4), 5, yappRight, yappSymmetric],
                  [(3*containerLength/4), 5, yappLeft, yappSymmetric],
                  [(containerWidth/2), 5, yappFront],
                  [(containerWidth/2), 5, yappBack]
                ];
               
//-- pushButtons  -- origin is pcb[0,0,0]
// (0) = posx
// (1) = posy
// (2) = capLength
// (3) = capWidth
// (4) = capAboveLid
// (5) = switchHeight
// (6) = switchTrafel
// (7) = poleDiameter
// (n) = buttonType  {yappCircle|yappRectangle}
pushButtons = [
                [calButtonRelZero[0], calButtonRelZero[1], 8, 8, 3, calButtonRelZero[2],   1, 3.5, yappCircle],
              ];     





// power board base
translate(pbZero - [0,0,pbBaseThickness]){
    difference(){
            // base
            translate([-pbWallThickness,0,0]){
                cube([pbWidth+2*pbWallThickness,pbLength+pbWallThickness,pbBaseThickness]);
            }

            // hole
            translate([0,-0.02,-1])
            cube([pbWidth,pbLength+0.02,pbBaseThickness+2]);
    }
}

difference(){
    union(){
        // main case
        YAPPgenerate();
        // button base
        translate(buttonZero - [buttonWallThickness, buttonWallThickness,0]){
            cube([buttonWidth+2*buttonWallThickness,buttonDepth+buttonWallThickness,buttonWidth+buttonWallThickness]);
        }
    }

    // standoffHoles
    translate(boardZero) translate([boardHoleWall + standoffPinDiameter/2,boardHoleWall + standoffPinDiameter/2,-standoffHeight]){
        xStep = boardWidth - 2*boardHoleWall - standoffPinDiameter;
        yStep = boardLength - 2*boardHoleWall - standoffPinDiameter;
        for(x=[0,xStep]) for(y=[0,yStep]) translate([y,x,0]) {
            cylinder(d=standoffPinDiameter+0.02, h = 2*standoffHeight_calc);
        }
    }

    // usbc case cutout
    translate(pbZero +[0,0,-pbZero[2]+bottomTopThickness]) translate([pbWidth/2,0,usbCHeight/2]) translate([0,0,pbBoardThickness+usbCHeight/2]){
        cube([usbCWidth, 20, usbCHeight], center=true);
    }

    // buttonCutout
    translate(buttonZero){
        // body cutout
        cube([buttonWidth, buttonDepth+wallThickness_calc+1, buttonWidth]);
        // leg cutouts
        translate([0,-buttonWallThickness-1,0]){
            cube([buttonWidth/4, buttonDepth+wallThickness_calc+1, buttonWidth]);
            translate([3*buttonWidth/4,0,0])
                cube([buttonWidth/4, buttonDepth+wallThickness_calc+1, buttonWidth]);
        }
    }

    // back grill
    grillWidth = 2;
    grillSpacing = 2;
    grillHeight = sqrt(containerHeight^2 + containerWidth^2);
    translate([-1, 2*wallThickness_calc, 2*bottomTopThickness]){
        intersection(){
            cube([wallThickness_calc+2,containerWidth-2*wallThickness_calc,containerHeight-4*bottomTopThickness-lidWallHeight]);
            union(){
                translate([0,containerWidth/2, -containerHeight/2]) rotate([45,0,0]) for(i = [0 : grillWidth+grillSpacing : grillHeight]){
                    translate([0,i,0]) cube([wallThickness_calc+2, grillWidth, grillHeight]);
                }
            }
        }
    }
}

