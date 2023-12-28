include <../../../../openscad/libs/NopSCADlib/lib.scad>


/*
--
topBottomThickness
--
generalPadding
--
lcdTopPinHeight
--
lcdPCBThickness
--
lcdBottomClearance // not needed
--
generalPadding // not needed
--
espMinHeight
-- 
espPcbThickness
--
espBottomClearance
--
topBottomThickness
-- 
*/


generalPadding = 4;

espMinHeight = 20;
espPCBThickness = 1.45;
espLength = 48;
espWidth = 25.7;
espBottomClearance = 5;

espHoleDiameter = 2.7;
espHoleWall = 0.8;

m2Hole = 2.2;
m3Hole = 3.4;
m4Hole = 4.2;

m4Hex = 7.7 + 0.45;
m4HexDepth = 3.1;

usbMicroWidth = 12;
usbMicroHeight = 7;
usbMicroY = 1.4; // from pcb

lcdHoleDiameter = 3.37;
lcdHoleWall = 1;
lcdLength = 99;
lcdWidth = 60;
lcdBottomClearance = 12.5;
lcdStandoffHeight = espBottomClearance+espPCBThickness+espMinHeight/*+generalPadding+lcdBottomClearance */;
lcdPCBThickness = 1.6;
lcdTopPinHeight = 4.9; // pins coming up through the pcb
lcdLeftClearance = 7.4; // i2c interface jumpers

// must be larger than lcdTopPinHeight
lcdTopStandoffHeight = 10;

lcdScreenVertical = 40;
lcdScreenHeight = 9.5;

wallThickness_calc = 2.0;
bottomTopThickness = 2.0;
paddingBack_calc         = generalPadding + lcdLeftClearance;
paddingFront_calc        = generalPadding;
paddingRight_calc        = generalPadding;
paddingLeft_calc         = generalPadding;

containerWidth = paddingBack_calc + lcdLength + paddingFront_calc;
containerHeight = paddingLeft_calc + lcdWidth + paddingRight_calc;
containerVertical = lcdStandoffHeight + lcdPCBThickness + lcdTopStandoffHeight;



lcdZero = [wallThickness_calc + paddingBack_calc, wallThickness_calc + paddingLeft_calc, bottomTopThickness];
lcdRelZero = [0,0,0];

espZero = [
    wallThickness_calc + paddingBack_calc + lcdLength - espLength - generalPadding, 
    wallThickness_calc + paddingLeft_calc + lcdWidth/2 - espWidth/2,
    bottomTopThickness
];
espRelZero = espZero - lcdZero;

// distance from back
MountHoleHeight = 1/3*containerVertical;

/*
translate([5.3,239.4,5]){
    difference(){
        cube([fanWidth, fanWidth, 7.75]);
        translate([fanHoleWall+3.12/2, fanHoleWall+3.12/2,-6])
            #cylinder(d=3.12, h=2*7,75);
        translate([fanWidth-fanHoleWall-3.12/2, fanHoleWall+3.12/2,-6])
            #cylinder(d=3.12, h=2*7,75);
        translate([fanWidth-fanHoleWall-3.12/2, fanWidth - fanHoleWall-3.12/2,-6])
            #cylinder(d=3.12, h=2*7,75);
        translate([fanHoleWall+3.12/2, fanWidth - fanHoleWall-3.12/2,-6])
            #cylinder(d=3.12, h=2*7,75);
    }
}

translate(espZero + [0,0,espBottomClearance]){
    #cube([espLength, espWidth, espPCBThickness]);
}

translate(lcdZero){
    translate([0,0,lcdStandoffHeight])
    #cube([lcdLength, lcdWidth, lcdPCBThickness+lcdTopPinHeight]);
    translate([0,lcdWidth/2-lcdScreenVertical/2,0])
        #cube([lcdLength, lcdScreenVertical, lcdStandoffHeight+lcdPCBThickness+lcdScreenHeight]);
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
pcbLength           = lcdLength;
pcbWidth            = lcdWidth;
pcbThickness        = lcdPCBThickness;
                            
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
standoffHeight      = 0.0;  //-- only used for showPCB
standoffPinDiameter = lcdHoleDiameter;
standoffHoleSlack   = 0.4;
standoffDiameter    = 2*lcdHoleDiameter;

//-- Total height of box = basePlaneThickness + lidPlaneThickness 
//--                     + baseWallHeight + lidWallHeight
//-- space between pcb and lidPlane :=
//--      (bottonWallHeight+lidWallHeight) - (standoffHeight+pcbThickness)
lidWallHeight       = 3;
baseWallHeight      = containerVertical - 3;

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
                   // lcd
                   [lcdRelZero[0] + lcdHoleDiameter/2 + lcdHoleWall, lcdRelZero[1] + lcdHoleDiameter/2+lcdHoleWall, lcdStandoffHeight, 0, yappBoth, yappBackLeft, yappAddFillet],
                   [lcdRelZero[0] + lcdLength - lcdHoleDiameter/2-lcdHoleWall, lcdRelZero[1] + lcdHoleDiameter/2+lcdHoleWall, lcdStandoffHeight, 0, yappBoth, yappBackLeft, yappAddFillet],
                   [lcdRelZero[0] + lcdLength - lcdHoleDiameter/2-lcdHoleWall, lcdRelZero[1] + lcdWidth - lcdHoleDiameter/2 - lcdHoleWall, lcdStandoffHeight, 0, yappBoth, yappBackLeft, yappAddFillet],
                   [lcdRelZero[0] + lcdHoleDiameter/2+lcdHoleWall, lcdRelZero[1] + lcdWidth - lcdHoleDiameter/2 - lcdHoleWall, lcdStandoffHeight, 0, yappBoth, yappBackLeft, yappAddFillet],

                   // esp
                   /*
                   [espRelZero[0] + espHoleWall + espHoleDiameter/2, espRelZero[1] + espHoleWall + standoffPinDiameter/2, espBottomClearance, 2, yappBaseOnly, yappBackLeft, yappAddFillet], 
                   [espRelZero[0] + espLength - espHoleWall - espHoleDiameter/2, espRelZero[1] + espHoleWall + standoffPinDiameter/2, espBottomClearance, 2, yappBaseOnly, yappBackLeft, yappAddFillet], 

                   [espRelZero[0] + espHoleWall + espHoleDiameter/2, espRelZero[1] + espWidth - espHoleWall - standoffPinDiameter/2, espBottomClearance, 2, yappBaseOnly, yappBackLeft, yappAddFillet], 
                   [espRelZero[0] + espLength - espHoleWall - espHoleDiameter/2, espRelZero[1] +espWidth - espHoleWall - standoffPinDiameter/2, espBottomClearance, 2, yappBaseOnly, yappBackLeft, yappAddFillet], 
                   */
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

/*
cutoutsGrill = [
                   [fanRelZero[0]+1.5*fanHoleOffset, fanRelZero[1]+1.5*fanHoleOffset, fanWidth-3*fanHoleOffset, fanWidth-3*fanHoleOffset, 2, 1.4,  45, "lid", 
                   [for (a = [0 : 50]) 0.5*fanWidth*[ cos(a*360/50)+1/2, sin(a * 360 / 50)+1/2 ]]
               ]];
cutoutsGrill = [
                   [
                       fanRelZero[0], fanRelZero[1], fanWidth, fanWidth, 3, 1.6,  45, "lid", 
                       [for (a = [0 : 50]) 0.5*fanBladeWidth*[ cos(a*360/50), sin(a * 360 / 50) ] + [fanWidth/2,fanWidth/2]]
                   ],
                ];
*/


//-- front plane  -- origin is pcb[0,0,0]
// (0) = posy
// (1) = posz
// (2) = width
// (3) = height
// (4) = angle
// (n) = { yappRectangle | yappCircle }
// (n) = { yappCenter }
cutoutsFront =  [
                    [containerHeight/2 - usbMicroWidth/2 + wallThickness_calc, 0.4 + espBottomClearance - usbMicroHeight/2 - usbMicroY, usbMicroWidth, usbMicroHeight, 0, yappRectangle, yappCenter],
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
                  [(1*containerWidth/4), 5, yappRight, yappSymmetric],
                  [(containerWidth/2), 5, yappLeft],
                  [(containerHeight/2), 5, yappFront],
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


module case(){
    espLegWidth = espHoleDiameter + 2*espHoleWall;
    difference(){
        union(){
            YAPPgenerate();

            // esp legs
            translate(espZero - [0,0,bottomTopThickness]){
                cube([espLegWidth, espLegWidth, espBottomClearance + bottomTopThickness]);
                translate([espLength - espLegWidth,0,0])
                    cube([espLegWidth, espLegWidth, espBottomClearance + bottomTopThickness]);
                translate([espLength - espLegWidth,espWidth - espLegWidth,0])
                    cube([espLegWidth, espLegWidth, espBottomClearance + bottomTopThickness]);

                translate([0,espWidth - espLegWidth,0])
                    cube([espLegWidth, espLegWidth, espBottomClearance + bottomTopThickness]);
            }
            // mountBlocks
            translate([wallThickness_calc, wallThickness_calc, bottomTopThickness])
                cube([standoffDiameter + paddingBack_calc + m4HexDepth, standoffDiameter+paddingLeft_calc, MountHoleHeight + m4Hole]);
            translate([wallThickness_calc+containerWidth - paddingFront_calc - standoffDiameter-m4HexDepth, wallThickness_calc, bottomTopThickness])
                cube([standoffDiameter + paddingFront_calc + m4HexDepth, standoffDiameter+paddingLeft_calc, MountHoleHeight + m4Hole]);

        } // end union

        // holes in case

        // espHoles
        translate(espZero + [0,0,-1 - bottomTopThickness]){
            holeOffset = espHoleWall + espHoleDiameter/2;
            translate([holeOffset, holeOffset,0])
                cylinder(d = m2Hole, h = espBottomClearance + bottomTopThickness + 2);

            translate([espLength-holeOffset, holeOffset,0])
                cylinder(d = m2Hole, h = espBottomClearance + bottomTopThickness + 2);

            translate([espLength-holeOffset, espWidth - holeOffset,0])
                cylinder(d = m2Hole, h = espBottomClearance + bottomTopThickness + 2);

            translate([holeOffset, espWidth - holeOffset,0])
                cylinder(d = m2Hole, h = espBottomClearance + bottomTopThickness + 2);
        }

        // mount Holes
        translate([-2,standoffDiameter,MountHoleHeight]) rotate([0,90,0])
            cylinder(d = m4Hole, h =containerWidth + 2*wallThickness_calc + 4);

        translate([standoffDiameter+paddingBack_calc+wallThickness_calc, standoffDiameter, MountHoleHeight]) rotate([0,90,0])
            cylinder($fn = 6, h = containerWidth-2*standoffDiameter-paddingBack_calc-paddingFront_calc, d = m4Hex,  center = false);

    }
}

module mount(){
    caseExternalWidth = 2*wallThickness_calc + containerWidth;
    caseExternalHeight = containerVertical + 2*bottomTopThickness;
    mt = 2*wallThickness_calc;
    md = 1.7*caseExternalHeight;
    baseWidth = caseExternalWidth + 2*mt+0.2;

    holeHeight = 1*sqrt(MountHoleHeight^2 + standoffDiameter^2);

    cube([baseWidth,md,mt]);

    difference(){
        union(){
            translate([0, caseExternalHeight - MountHoleHeight,0]) {
                translate([0,-3*m4Hole/2,0])
                    cube([baseWidth, 3*m4Hole, holeHeight + mt]);
                translate([0,0,holeHeight+mt]) rotate([0,90,0])
                    cylinder(d = 3*m4Hole, h = baseWidth);
            }
        }

        translate([mt,0,0]){
            cube([baseWidth - 2*mt, md, caseExternalHeight]);
        }
        translate([-1,caseExternalHeight - MountHoleHeight,holeHeight+mt]) rotate([0,90,0])
            cylinder(d = m4Hole, h = baseWidth + 2);
    }
}


case();
translate([-2*wallThickness_calc,-90,0])
mount();

