include <../../../openscad/libs/NopSCADlib/lib.scad>

fanWidth = 30;
fanHeight = 7.8;
fanHoleWall = 1.6;
m3Hole = 3.1;

bbLength = 86;
bbWidth = 46.5;
bbMinHeight = 26;
bbThickness = 9.6;

bbButtonX = 26;
// relative to bottomLeft of bb
bbButton1Y = 58.2;
bbButton2Y = 76;
bbButtonZ = 14.12;

bbPadding = 5;

rpiLength = 85;
rpiWidth = 56;

rpiHoleDiameter = 2.5;
rpiHoleWall = 2.3;
rpiMinHeight = 22;
rpiStandoffHeight = 5;
rpiPCBThickness = 1.5;
// amount ports stick out
rpiPortDepth = 3;
rpiPortWidth = 32;
rpiPortHeight = 15.6;
usbcWidth = 15;
usbcHeight = 9;

lcdHoleDiameter = 3.37;
lcdHoleWall = 1;
lcdLength = 99;
lcdWidth = 60;
lcdStandoffHeight = 18; // min is 10
lcdPCBThickness = 1.6;
lcdTopPinHeight = 4.9; // pins coming up through the pcb
lcdLeftClearance = 7.4; // i2c interface jumpers

lcdScreenVertical = 40;
lcdScreenHeight = 9.5;

wallThickness_calc = 2.0;
bottomTopThickness = 2.0;
generalPadding = 4;
paddingBack_calc         = lcdLength - rpiLength + bbWidth + generalPadding + bbPadding;
paddingFront_calc        = rpiPortDepth - wallThickness_calc+1;
paddingRight_calc        = lcdWidth + 3*generalPadding;
paddingLeft_calc         = generalPadding;

containerWidth = paddingBack_calc + rpiLength + paddingFront_calc;
containerHeight = paddingLeft_calc + paddingRight_calc + rpiWidth;

/*
translate([wallThickness_calc,wallThickness_calc,bottomTopThickness]){
    //cube([bbWidth, bbLength, bbMinHeight]);
    translate([bbButtonX, bbButton1Y,0])
        cylinder(d=3.6,h=bbButtonZ);
    translate([bbButtonX, bbButton2Y,0])
        cylinder(d=3.6,h=bbButtonZ);
}
*/


piZero = [wallThickness_calc + paddingBack_calc, wallThickness_calc + paddingLeft_calc, bottomTopThickness];

lcdZero = [containerWidth-lcdLength+wallThickness_calc - 4,
           rpiWidth+wallThickness_calc+2 + 2*generalPadding,
           bottomTopThickness];
lcdRelZero = lcdZero - piZero;

fanZero = [wallThickness_calc + bbWidth/2 - fanWidth/2, wallThickness_calc + bbLength/4 - fanWidth / 2,0];
fanRelZero = fanZero - piZero;

/*
translate(lcdZero){
    #cube([lcdLength, lcdWidth, lcdStandoffHeight+lcdPCBThickness+lcdTopPinHeight]);
    translate([0,lcdWidth/2-lcdScreenVertical/2,0])
        #cube([lcdLength, lcdScreenVertical, lcdStandoffHeight+lcdPCBThickness+lcdScreenHeight]);
}
translate(piZero + [rpiLength/2, rpiWidth/2 ,standoffHeight])
    pcb(RPI4);
*/

include <../../../openscad/libs/YAPP_Box/library/YAPPgenerator_v21.scad>

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
pcbLength           = rpiLength;
pcbWidth            = rpiWidth;
pcbThickness        = rpiPCBThickness;
                            
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
standoffPinDiameter = rpiHoleDiameter;
standoffHoleSlack   = 0.4;
standoffDiameter    = 2*lcdHoleDiameter;

//-- Total height of box = basePlaneThickness + lidPlaneThickness 
//--                     + baseWallHeight + lidWallHeight
//-- space between pcb and lidPlane :=
//--      (bottonWallHeight+lidWallHeight) - (standoffHeight+pcbThickness)
lidWallHeight       = 3;
baseWallHeight      = bbMinHeight - 3 + generalPadding;

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
                   // rpi
                   [23.5, rpiHoleWall + standoffPinDiameter/2, standoffHeight, 0, yappBoth, yappFrontLeft], 
                   [rpiHoleWall+standoffPinDiameter/2, rpiHoleWall+standoffPinDiameter/2, standoffHeight, 0, yappBoth, yappBackRight],

                   [23.5, rpiHoleWall+standoffPinDiameter/2, standoffHeight, 0, yappBoth, yappFrontRight],
                   [rpiHoleWall+standoffPinDiameter/2, rpiHoleWall+standoffPinDiameter/2, standoffHeight, 0, yappBoth, yappBackLeft],

                   // lcd
                   [lcdRelZero[0] + lcdHoleDiameter/2 + lcdHoleWall, lcdRelZero[1] + lcdHoleDiameter/2+lcdHoleWall, lcdStandoffHeight, 0, yappBoth, yappBackLeft],
                   [lcdRelZero[0] + lcdLength - lcdHoleDiameter/2-lcdHoleWall, lcdRelZero[1] + lcdHoleDiameter/2+lcdHoleWall, lcdStandoffHeight, 0, yappBoth, yappBackLeft],
                   [lcdRelZero[0] + lcdLength - lcdHoleDiameter/2-lcdHoleWall, lcdRelZero[1] + lcdWidth - lcdHoleDiameter/2 - lcdHoleWall, lcdStandoffHeight, 0, yappBoth, yappBackLeft],
                   [lcdRelZero[0] + lcdHoleDiameter/2+lcdHoleWall, lcdRelZero[1] + lcdWidth - lcdHoleDiameter/2 - lcdHoleWall, lcdStandoffHeight, 0, yappBoth, yappBackLeft],
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
                    // fan screw holes
                    [fanRelZero[0], fanRelZero[1], m3Hole, 24, 0, yappCircle],
                    [fanRelZero[0]+fanWidth-2*fanHoleWall, fanRelZero[1], m3Hole, 0, 0, yappCircle],
                    [fanRelZero[0]+fanWidth-2*fanHoleWall, fanRelZero[1]+fanWidth-2*fanHoleWall, m3Hole, 0, 0, yappCircle],
                    [fanRelZero[0], fanRelZero[1]+fanWidth-2*fanHoleWall, m3Hole, 0, 0, yappCircle],

                    [lcdRelZero[0], lcdRelZero[1]+ lcdWidth/2 - lcdScreenVertical/2, lcdScreenVertical, lcdLength, 0, yappRectangle],
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
                   [fanRelZero[0], fanRelZero[1]+m3Hole/2, fanWidth-2*m3Hole, fanWidth-3*m3Hole/2, 2, 1.6,  0, "lid"]
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
                    [1, -1.5, rpiPortWidth/2, rpiPortHeight+2.5, 0, yappRectangle],
                    [rpiPortWidth/2+3, -1.5, rpiPortWidth/2, rpiPortHeight+2.5, 0, yappRectangle],

                    [rpiPortWidth+5.3, -0.7, 17, 14.5, 0, yappRectangle],
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
                    [11.2, 0.5, usbcWidth, usbcHeight, 0, yappRectangle, yappCenter],
                    [39.7, 0.5, usbcWidth, usbcHeight, 0, yappRectangle, yappCenter]
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
                  [(1*containerHeight/4), 5, yappBack, yappSymmetric],
                  [(3*containerHeight/4), 5, yappFront, yappSymmetric],
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
                [-piZero[0]+wallThickness_calc+bbButtonX, bbButton1Y-4, 8, 8, 3, bbButtonZ-rpiStandoffHeight-rpiPCBThickness-bottomTopThickness+0.5,   1, 3.5, yappCircle],
                [-piZero[0]+wallThickness_calc+bbButtonX, bbButton2Y-4, 8, 8, 3, bbButtonZ-rpiStandoffHeight-rpiPCBThickness- bottomTopThickness+0.5,   1, 3.5, yappCircle],
              ];     


YAPPgenerate();
