

$fn=15;

bbLength = 86;
bbWidth = 46.5;
bbMaxHeight = 23;

mcMaxHeight = 27;

m2Hole = 1.95;

include <../libs/YAPP_Box/library/YAPPgenerator_v21.scad>

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
pcbLength           = 43.9;
pcbWidth            = 43.9;
pcbThickness        = 1.2;
                            
//-- padding between pcb and inside wall
paddingFront        = 3;
paddingBack         = 15;
paddingRight        = 70;
paddingLeft         = 14;

//-- Edit these parameters for your own box dimensions
wallThickness       = 2.0;
basePlaneThickness  = 1.0;
lidPlaneThickness   = 1.0;


//-- ridge where base and lid off box can overlap
//-- Make sure this isn't less than lidWallHeight
ridgeHeight         = 3.0;
ridgeSlack          = 0.2;
roundRadius         = 2.0;

//-- How much the PCB needs to be raised from the base
//-- to leave room for solderings and whatnot
standoffHeight      = 5.0;  //-- only used for showPCB
standoffPinDiameter = 2.7;
standoffHoleSlack   = 0.4;
standoffDiameter    = 5.8;

//-- Total height of box = basePlaneThickness + lidPlaneThickness 
//--                     + baseWallHeight + lidWallHeight
//-- space between pcb and lidPlane :=
//--      (bottonWallHeight+lidWallHeight) - (standoffHeight+pcbThickness)
lidWallHeight       = 8;
baseWallHeight      = 5 + 1.2 - 8 + 27 + 1;

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
                   [1.5+standoffPinDiameter/2, 1.5 + standoffPinDiameter/2, standoffHeight, 0, yappBoth, yappFrontLeft], 
                   [1.5+standoffPinDiameter/2, 1.5+standoffPinDiameter/2, standoffHeight, 0, yappBoth, yappBackRight, yappAddFillet],
                   [1.5+standoffPinDiameter/2, 1.5+standoffPinDiameter/2, standoffHeight, 0, yappBoth, yappFrontRight, yappAddFillet],
                   [1.5+standoffPinDiameter/2, 1.5+standoffPinDiameter/2, standoffHeight, 0, yappBoth, yappBackLeft, yappAddFillet]
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
             //       [30, 0, 10, 24, yappRectangle]
             //     , [pcbLength/2, pcbWidth/2, 12, 4, yappCircle]
             //     , [pcbLength-8, 25, 10, 14, yappRectangle, yappCenter]
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
             //     [20, 0, 10, 24, 0, yappRectangle]
             //   , [pcbWidth-6, 40, 12, 4, 20, yappCircle]
             //   , [30, 25, 10, 14, 45, yappRectangle, yappCenter]
                ];

//-- cutoutsGrill    -- origin is pcb[0,0,0]
// (0) = xPos
// (1) = yPos
// (2) = grillWidth
// (3) = grillLength
// (4) = gWidth
// (5) = gSpace
// (6) = gAngle
// (7) = plane { "base" | "led" }
// (7) = {polygon points}}
//

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
                //[0,  5, 60, 40, 2, 2,  0, "base"],
                [9, 5, 68, 25, 3, 2,  45, "lid"]
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
              //    [25, -3, 37, 17, 0, yappRectangle, yappMinCutout]
              //    , [30, 7.5, 15, 9, 0, yappRectangle, yappCenter]
              //    , [0, 2, 10, 0, 0, yappCircle]
            
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
              //      [10, 0, 10, 18, 0, yappRectangle]
              //    , [30, 0, 10, 8, 0, yappRectangle, yappCenter]
              //    , [pcbWidth, 0, 8, 0, 0, yappCircle]
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
              [-paddingBack/2, -standoffHeight+6, 8.5, 8.5, 0, yappCircle, yappCenter],
              [pcbWidth/2, -standoffHeight+6, 7, 7, 0, yappCircle, yappCenter]
              //    , [30, 5, 25, 10, 0, yappRectangle, yappCenter]
              //    , [pcbLength-10, 2, 10, 0, 0, yappCircle]
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
              //      [0, 0, 15, 7, 0, yappRectangle]
              //    , [30, 10, 25, 15, 0, yappRectangle, yappCenter]
              //    , [pcbLength-10, 2, 10, 0, 0, yappCircle]
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
                //[25, 10, 5, 2.5, 5, 4.0, 6, 2, yappConnWithPCB, yappFrontRight, yappBackLeft, yappBackRight, yappAddFillet]
               //,[18, 20, 5, 2.5, 5, 5.0, 6, 5.5, yappAllCorners, yappAddFillet]
             // , [18, 20, 5, 2.5, 5, 4.0, 15, 0, yappConnWithPCB, yappFrontRight, yappBackLeft, yappBackRight, yappAddFillet]
             // , [18, 20, 5, 2.5, 5, 4.0, 6, 0, yappConnWithPCB, yappFrontLeft, yappAddFillet]
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
                  //  [45, 3.3, 10, 3, yappFront, yappLeft, yappRight, yappAddFillet]//, yappCenter]
                  //, [10, 6, 10, 3, yappBack, yappFront]
              //    , [4, 3, 34, 3, yappFront]
              //    , [25, 3, 3, 3, yappBack]
                ];

//-- snap Joins -- origen = box[x0,y0]
// (0) = posx | posy
// (1) = width
// (n) = yappLeft / yappRight / yappFront / yappBack (one or more)
// (n) = { yappSymmetric }
snapJoins   =   [
                  [(2*pcbWidth/3), 5, yappBack, yappSymmetric],
                  [(2*pcbWidth/3), 5, yappFront, yappSymmetric]
                //, [(pcbLength/2)+6, 3, yappLeft]
                //, [(pcbLength/2)+6, 3, yappRight]

              //    [2,               5, yappLeft, yappRight, yappSymmetric]
              //    [5,              10, yappLeft]
              //  , [shellLength-2,  10, yappLeft]
              //  , [20,             10, yappFront, yappBack]
              //  , [2.5,             5, yappBack,  yappFront, yappSymmetric]
                ];
               



// mb stands for motherboard
mbHoleDiameter = 2.2;
// mb height/width are hole to hole
mbHeight = 52.5 + mbHoleDiameter;
mbWidth = 32.75 + mbHoleDiameter;
mbStandoffHeight = standoffHeight;

// zero for first mb Hole
mbZero = [wallThickness+paddingBack+4, wallThickness+paddingLeft+pcbLength+8, basePlaneThickness];
mcZero = [wallThickness+paddingBack, wallThickness+paddingLeft, basePlaneThickness];

mbRelZero = mbZero - mcZero;

buttonsX = 26.4+mbRelZero[0]+mbHoleDiameter/2;
buttonY1 = 30.2+mbRelZero[1]+mbHoleDiameter/2;
buttonY2 = 47.6+mbRelZero[1]+mbHoleDiameter/2;

echo("=====================");
echo("=====================");
echo(buttonsX);
echo(buttonY1);
echo(buttonY2);
echo(mbStandoffHeight + 8);
echo("=====================");
echo("=====================");

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

// hard coded values are set based on prints above, openscad seems to have a bug where the vars are undefined
pushButtons = [
                [31.5, 83.2, 8, 8, 3, 13-pcbThickness-standoffHeight,   1, 3.5, yappCircle],
                [31.5, 100.6, 8, 8, 3, 13-pcbThickness-standoffHeight,   1, 3.5, yappCircle]
              ];     

union(){
    YAPPgenerate();
    translate([wallThickness,31+wallThickness,basePlaneThickness]){
        cube([paddingBack,wallThickness,1.5]);
    }


    translate(mbZero){
        for(x=[0,mbWidth], y=[0,mbHeight]) translate([x,y,0]){
            difference(){
                cylinder(d=4, h = mbStandoffHeight);
                cylinder(d=m2Hole, h = mbStandoffHeight+1);
            }
        }
    }
}
