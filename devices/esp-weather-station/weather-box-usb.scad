include <../../../../openscad/libs/NopSCADlib/lib.scad>

espLength = 48;
espWidth = 25.7;

espHoleDiameter = 2.7;
espHoleWall = 0.8;

espMinHeight = 20;
espPCBThickness = 1.45;

dupont4Width = 10.4;
dupont1Height = 2.76;

usbMicroWidth = 12;
usbMicroHeight = 7;
usbMicroY = 1.4; // from pcb

wallThickness_calc = 2.0;
bottomTopThickness = 2.0;
generalPadding = 4;

paddingBack_calc         = generalPadding;
paddingFront_calc        = generalPadding + 15;
paddingRight_calc        = generalPadding;
paddingLeft_calc         = generalPadding;

containerWidth = paddingBack_calc + espLength + paddingFront_calc;
containerHeight = paddingLeft_calc + paddingRight_calc + espWidth;

/*
translate([wallThickness_calc+paddingBack_calc, wallThickness_calc + paddingLeft_calc, standoffHeight+bottomTopThickness]){
    difference(){
        cube([espLength, espWidth, espPCBThickness]);
        translate([espHoleDiameter/2 + espHoleWall, espHoleDiameter/2 + espHoleWall,0])
            #cylinder(d=espHoleDiameter, h = 100);

        translate([-espHoleDiameter/2 - espHoleWall+espLength, espHoleDiameter/2 + espHoleWall,0])
            #cylinder(d=espHoleDiameter, h = 100);

        translate([-espHoleDiameter/2 - espHoleWall+espLength, espHoleDiameter/2 + espHoleWall,0])
            #cylinder(d=espHoleDiameter, h = 100);
    }
}
*/

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
pcbLength           = espLength;
pcbWidth            = espWidth;
pcbThickness        = espPCBThickness;
                            
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
standoffHeight      = 5.0;  //-- only used for showPCB
standoffPinDiameter = espHoleDiameter;
standoffHoleSlack   = 0.4;
standoffDiameter    = 4;

//-- Total height of box = basePlaneThickness + lidPlaneThickness 
//--                     + baseWallHeight + lidWallHeight
//-- space between pcb and lidPlane :=
//--      (bottonWallHeight+lidWallHeight) - (standoffHeight+pcbThickness)
lidWallHeight       = 3;
baseWallHeight      = espMinHeight + generalPadding;

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
                   // esp
                   [espHoleWall+standoffPinDiameter/2, espHoleWall+standoffPinDiameter/2, standoffHeight, 2, yappBoth, yappAllCorners, yappAddFillet], 
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

cutoutsGrill = [];


//-- front plane  -- origin is pcb[0,0,0]
// (0) = posy
// (1) = posz
// (2) = width
// (3) = height
// (4) = angle
// (n) = { yappRectangle | yappCircle }
// (n) = { yappCenter }
cutoutsFront =  [
                    [containerHeight/2+wallThickness/2-dupont4Width/2, 0, dupont4Width, dupont1Height, 0, yappRectangle, yappCenter],
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
               [ containerHeight/2, standoffHeight+dupont1Height+pcbThickness+5/2+0.35,   0, 1, "front", "Liberation Mono:style", 4, "▲" ],
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
                    [containerHeight/2 - usbMicroWidth + wallThickness, -usbMicroHeight/2-espPCBThickness-usbMicroY, usbMicroWidth, usbMicroHeight, 0, yappRectangle],
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
                  [(1*containerWidth/4), 5, yappRight, yappSymmetric],
                  [(3*containerWidth/4), 5, yappLeft, yappSymmetric]
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
              ];     


YAPPgenerate();
