include <../../../../../openscad/libs/BOSL2/std.scad>

$fn=100;

roundingRadius = 2;
wallThickness = 1.6;

generalPadding = 2;
boardHeight = 37;
boardWidth = 44.5;
boardDepth = 16.9;

boardPaddingLeft = 2.4 + 2.2;
boardMarginLeft = 8.4;
screenCenterX = boardPaddingLeft + boardMarginLeft  + boardWidth/2;
screenCenterY = 2.3;
screenShift = 0.5;
usbShift = 0.6;

screenWidth = 34.4;
screenHeight = 35;

usbAWidth = 12.2;
usbADepth = 5.4;
usbADepthMargin = 3;

m2Hole = 2;

caseWidth = boardWidth + boardMarginLeft + 2*generalPadding;
caseHeight = boardHeight + 2*generalPadding;
caseDepth = boardDepth;

screenPadding = 0.8;


// translate([boardWidth/2 + wallThickness + boardPaddingLeft, 0,0])
// #cube([boardWidth, boardHeight,boardDepth], anchor=CENTER+BOTTOM);

difference(){
    // main box
    translate([0,-(caseHeight+2*wallThickness)/2,0]){
        difference(){
            cuboid([caseWidth+2*wallThickness,caseHeight+2*wallThickness+screenCenterY,caseDepth+wallThickness], rounding=roundingRadius, anchor=BOTTOM+FRONT+LEFT);
            translate([wallThickness, wallThickness, -1])
                cube([caseWidth,caseHeight+screenCenterY,caseDepth+1]);
        }
    }

    // usb cutout
    translate([0,usbShift,0])
        cube([usbAWidth,usbAWidth,usbADepth+usbADepthMargin], anchor=CENTER+BOTTOM);

    // screen cutout
    translate([screenCenterX,screenCenterY,0]) {
        translate([0,screenShift,0])
            cube([screenWidth+screenPadding, screenHeight+screenPadding, caseDepth + 10], anchor=CENTER+BOTTOM);
        xOffset = boardWidth/2-2.5;
        yOffset = boardHeight/2-2.5;
        for(x=[-xOffset, +xOffset]) for(y=[-yOffset, yOffset]) translate([x,y,0])
        cylinder(d=m2Hole, h=caseDepth+10);
    }
}
